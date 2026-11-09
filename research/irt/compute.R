suppressPackageStartupMessages(library(mirt))
suppressPackageStartupMessages(library(jsonlite))
args <- commandArgs(trailingOnly=TRUE)
input <- fromJSON(args[1], simplifyVector=FALSE)
policy <- input$policy
set.seed(policy$engine$seed)
options(mc.cores=1)
dat <- do.call(rbind,lapply(input$matrix,function(row) vapply(row,function(x) if(is.null(x)) NA_real_ else as.numeric(x),numeric(1))))
colnames(dat) <- vapply(input$items, `[[`, '', 'questionVersionId')
groupIds <- unlist(input$groupOrder)
groupLabels <- paste0('G',seq_along(groupIds))
groups <- factor(groupLabels[match(unlist(input$groups),groupIds)],levels=groupLabels)
types <- vapply(input$items,function(x) if(x$modelFamily=='2PL') '2PL' else 'gpcm','')
fit <- function(invariance, se=TRUE) {
  if(length(groupIds)==1) return(mirt(dat,1,itemtype=types,method='EM',
    quadpts=policy$engine$quadrature,TOL=policy$engine$tolerance,
    SE=se,SE.type='Oakes',verbose=FALSE,technical=list(NCYCLES=policy$engine$maxIterations)))
  multipleGroup(dat,1,group=groups,itemtype=types,
    invariance=c(invariance,'free_means','free_var'), method='EM',
    quadpts=policy$engine$quadrature, TOL=policy$engine$tolerance,
    SE=se,SE.type='Oakes',verbose=FALSE,
    technical=list(NCYCLES=policy$engine$maxIterations))
}
stage <- 'FIT'
result <- tryCatch({
  model <- fit(colnames(dat))
  stage <- 'COVARIANCE'
  covariance <- vcov(model)
  parameterTable <- mod2values(model)
  estimated <- parameterTable[parameterTable$est,,drop=FALSE]
  atBoundary <- any((is.finite(estimated$lbound) & estimated$value-estimated$lbound<=1e-5) |
                    (is.finite(estimated$ubound) & estimated$ubound-estimated$value<=1e-5))
  identified <- isTRUE(extract.mirt(model,'converged')) && all(is.finite(covariance)) &&
    all(is.finite(estimated$value)) && !atBoundary &&
    min(eigen((covariance+t(covariance))/2,symmetric=TRUE,only.values=TRUE)$values)>0
  estimates <- list()
  diagnostics <- list()
  for (g in seq_along(levels(groups))) {
    stage <- paste0('GROUP_',g)
    group <- levels(groups)[g]
    gm <- if(length(groupIds)==1) model else extract.group(model,g)
    active <- which(colSums(!is.na(dat[groups==group,,drop=FALSE]))>0)
    # Rebuild a fixed-parameter model over administered columns only. This avoids
    # interpreting structural NA columns as omitted answers in S-X2 and Q3.
    gd <- dat[groups==group,active,drop=FALSE]
    pars <- mirt(gd,1,itemtype=types[active],pars='values',verbose=FALSE)
    for(j in seq_along(active)) {
      item <- extract.item(gm,active[j])
      idx <- which(pars$item==colnames(gd)[j])
      fixedValues <- item@par
      probabilityParameters <- item@parnames %in% c('g','u')
      fixedValues[probabilityParameters] <- plogis(fixedValues[probabilityParameters])
      pars$value[idx] <- unname(fixedValues[match(pars$name[idx],item@parnames)])
    }
    groupMean <- coef(gm,simplify=TRUE)$means[1]
    variance <- coef(gm,simplify=TRUE)$cov[1,1]
    pars$value[pars$name=='MEAN_1'] <- groupMean
    pars$value[pars$name=='COV_11'] <- variance
    pars$est <- FALSE
    if(anyNA(pars$value)) stop(paste('Fixed parameter mapping missing:',paste(unique(pars$name[is.na(pars$value)]),collapse=','),
                                   'available:',paste(extract.item(gm,active[1])@parnames,collapse=',')))
    fixed <- mirt(gd,1,itemtype=types[active],pars=pars,verbose=FALSE)
    stage <- paste0('GROUP_FIT_',g)
    sx <- tryCatch(itemfit(fixed,fit_stats='S_X2',na.rm=TRUE),error=function(e) NULL)
    q3 <- tryCatch(residuals(fixed,type='Q3',verbose=FALSE),error=function(e) NULL)
    adjusted <- NULL
    if(!is.null(q3)) {
      q3[lower.tri(q3,diag=TRUE)] <- NA
      adjusted <- q3-mean(q3,na.rm=TRUE)
    }
    pvalues <- if(!is.null(sx)) p.adjust(sx$p.S_X2,method='holm') else rep(NA_real_,length(active))
    for(j in seq_along(active)) {
      stage <- paste0('PARAMETER_',g,'_',j)
      index <- active[j]
      qid <- colnames(dat)[index]
      item <- extract.item(gm,index)
      picked <- which(item@parnames=='a1' | grepl('^d[1-9][0-9]*$',item@parnames) |
                      (types[index]=='2PL' & item@parnames=='d'))
      cov <- mirt:::subset_vcov(item,covariance)[picked,picked,drop=FALSE]
      if(is.null(estimates[[qid]])) estimates[[qid]] <- list(a=unname(item@par[picked[1]]),
        intercepts=I(unname(item@par[picked[-1]])), covariance=lapply(unname(split(cov,row(cov))),I),
        probabilityGrid=unname(split(probtrace(item,matrix(seq(-4,4,length.out=17))),row(probtrace(item,matrix(seq(-4,4,length.out=17)))))))
      maxq <- if(is.null(adjusted)) NA_real_ else max(c(adjusted[j,],adjusted[,j]),na.rm=TRUE)
      if(!is.finite(maxq)) maxq <- NA_real_
      diagnostics[[paste(groupIds[g],qid,sep=':')]] <- list(group=groupIds[g],questionVersionId=qid,
        sx2AdjustedP=if(is.finite(pvalues[j])) pvalues[j] else NULL,
        adjustedQ3=if(is.finite(maxq)) maxq else NULL)
    }
  }
  # Anchor release sensitivity. Structural focal NA remain constrained, while
  # one genuinely shared anchor at a time is allowed to differ across groups.
  anchors <- unlist(input$anchors)
  stage <- 'ANCHOR_RELEASE'
  anchorChecks <- list()
  for(anchor in anchors) {
    if(length(groupIds)==1) {
      anchorChecks[[anchor]] <- list(evaluated=FALSE,reason='REFERENCE_ONLY_NO_LINK_REQUIRED')
      next
    }
    released <- tryCatch(fit(setdiff(colnames(dat),anchor),FALSE),error=function(e) NULL)
    if(is.null(released) || !isTRUE(extract.mirt(released,'converged'))) {
      anchorChecks[[anchor]] <- list(evaluated=FALSE)
      next
    }
    lr <- tryCatch(anova(model,released),error=function(e) NULL)
    shifted <- list()
    for(g in seq_along(levels(groups))) {
      it <- extract.item(extract.group(released,g),match(anchor,colnames(dat)))
      a <- unname(it@par[it@parnames=='a1'])
      d <- unname(it@par[grepl('^d([1-9][0-9]*)?$',it@parnames)])
      if(length(d)>1 && d[1]==0) d <- d[-1]
      shifted[[g]] <- list(a=a,steps=-diff(c(0,d))/a)
    }
    base <- shifted[[1]]
    anchorChecks[[anchor]] <- list(evaluated=!is.null(lr),p=if(!is.null(lr)) tail(lr$p,1) else NULL,
      maximumLogSlopeDifference=max(vapply(shifted,function(x) abs(log(x$a/base$a)),0.0)),
      maximumStepDifference=max(vapply(shifted,function(x) max(abs(x$steps-base$steps)),0.0)))
  }
  rawP <- vapply(anchorChecks,function(x) if(is.null(x$p)||!is.finite(x$p)) NA_real_ else x$p,0.0)
  adjustedP <- p.adjust(rawP,method='holm')
  for(j in seq_along(anchorChecks)) anchorChecks[[j]]$holmP <- if(is.finite(adjustedP[j])) adjustedP[j] else NULL
  list(converged=identified,atParameterBoundary=atBoundary,estimates=estimates,fit=diagnostics,anchors=anchorChecks,
       engine=list(R=as.character(getRversion()),mirt=as.character(packageVersion('mirt'))))
},error=function(e) list(converged=FALSE,scientificFailure='MODEL_CONVERGENCE_FAILED',engineStage=stage,engineError=conditionMessage(e),engineCall=paste(deparse(conditionCall(e)),collapse=' ')))
write_json(result,args[2],auto_unbox=TRUE,null='null',na='null',digits=16)
