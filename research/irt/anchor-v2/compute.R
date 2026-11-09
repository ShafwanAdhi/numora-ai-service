# Separate, disabled-by-default research engine. Legacy compute.R is immutable.
suppressPackageStartupMessages(library(mirt))
suppressPackageStartupMessages(library(jsonlite))
args <- commandArgs(trailingOnly=TRUE)
input <- fromJSON(args[1],simplifyVector=FALSE)
policy <- input$policy
set.seed(policy$engine$seed)
options(mc.cores=1)
dat <- do.call(rbind,lapply(input$matrix,function(row) vapply(row,function(x) if(is.null(x)) NA_real_ else as.numeric(x),0.)))
colnames(dat) <- vapply(input$items,`[[`,'','questionVersionId')
groupIds <- unlist(input$groupOrder)
groups <- factor(paste0('G',match(unlist(input$groups),groupIds)),levels=paste0('G',seq_along(groupIds)))
types <- vapply(input$items,function(x) if(x$modelFamily=='2PL') '2PL' else 'gpcm','')
anchors <- unlist(input$anchors)

fit <- function(invariance) {
  multipleGroup(dat,1,group=groups,itemtype=types,
    invariance=c(invariance,'free_means','free_var'),method='EM',
    quadpts=policy$engine$quadrature,TOL=policy$engine$tolerance,
    SE=TRUE,SE.type='Oakes',verbose=FALSE,
    technical=list(NCYCLES=policy$engine$maxIterations))
}

item_indices <- function(rows,lookup) {
  picked <- which(rows$name=='a1' | rows$name=='d' | grepl('^d[1-9][0-9]*$',rows$name))
  # Fixed GPCM d0=0 is deliberately excluded; do not infer it from its value.
  indexes <- unname(lookup[as.character(rows$parnum[picked])])
  if(anyNA(indexes)) stop('PARAMETER_MAPPING_UNAVAILABLE')
  list(a=as.integer(indexes[1]),intercepts=I(as.integer(indexes[-1])))
}

model_block <- function(model, target=NULL, original_only=FALSE) {
  covariance <- vcov(model)
  table <- mod2values(model)
  labels <- colnames(covariance)
  # mirt 1.48 labels identify EACH parnum sharing a covariance coordinate:
  # a1.1.230 means both constrained group parameters use the same column.
  aliases <- lapply(strsplit(labels,'.',fixed=TRUE),function(parts) as.integer(parts[-1]))
  lookup <- setNames(rep(seq_along(aliases)-1L,lengths(aliases)),as.character(unlist(aliases)))
  values <- vapply(aliases,function(ids) {
    matches <- table$value[match(ids,table$parnum)]
    if(anyNA(matches) || max(abs(matches-matches[1]))>1e-8) stop('CONSTRAINT_MAPPING_UNAVAILABLE')
    matches[1]
  },0.)
  estimated <- table[table$est,,drop=FALSE]
  boundary <- any((is.finite(estimated$lbound) & estimated$value-estimated$lbound<=1e-5) |
                  (is.finite(estimated$ubound) & estimated$ubound-estimated$value<=1e-5))
  covariance_ok <- all(is.finite(covariance)) &&
    isTRUE(all.equal(covariance,t(covariance),tolerance=1e-8,check.attributes=FALSE)) &&
    min(eigen((covariance+t(covariance))/2,symmetric=TRUE,only.values=TRUE)$values)>0
  mapping <- list(); items <- list(); latent <- list(); oracle <- list()
  count <- if(original_only) 1L else length(groupIds)
  for(g in seq_len(count)) {
    gm <- if(original_only) model else extract.group(model,g)
    coefficients <- coef(gm,simplify=TRUE)
    latent[[groupIds[g]]] <- list(mean=unname(coefficients$means[1]),variance=unname(coefficients$cov[1,1]))
    ids <- colnames(dat)
    if(original_only) ids <- colnames(dat)[colSums(!is.na(dat[groups==levels(groups)[1],,drop=FALSE]))>0]
    actual <- list(); traces <- list()
    for(j in seq_along(ids)) {
      # extract.group() renumbers @parnum to its local group! Only the full
      # mod2values table retains authoritative multipleGroup covariance IDs.
      rows <- table[table$item==ids[j] & (original_only | table$group==levels(groups)[g]),,drop=FALSE]
      actual[[ids[j]]] <- item_indices(rows,lookup)
      if(is.null(target) || ids[j]==target) {
        trace <- probtrace(extract.item(gm,j),matrix(c(-2,0,2)))
        traces[[ids[j]]] <- lapply(seq_len(nrow(trace)),function(k) I(unname(trace[k,])))
      }
      if(!is.null(target) && ids[j]==target) mapping[[groupIds[g]]] <- actual[[ids[j]]]
    }
    items[[groupIds[g]]] <- actual
    oracle[[groupIds[g]]] <- traces
  }
  parameter_map <- lapply(seq_len(nrow(table)),function(i) list(
    group=as.character(table$group[i]),item=as.character(table$item[i]),name=as.character(table$name[i]),
    parnum=table$parnum[i],estimated=table$est[i],
    covarianceIndex=if(as.character(table$parnum[i]) %in% names(lookup)) unname(lookup[as.character(table$parnum[i])]) else NULL))
  list(converged=isTRUE(extract.mirt(model,'converged')) && covariance_ok && all(is.finite(values)),
       atParameterBoundary=boundary,values=I(unname(values)),
       covariance=lapply(seq_len(nrow(covariance)),function(i) I(unname(covariance[i,]))),
       covarianceLabels=I(labels),parameterMap=parameter_map,mapping=mapping,items=items,latent=latent,probabilityOracle=oracle,
       logLikelihood=as.numeric(logLik(model)))
}

stage <- 'VALIDATE'
result <- tryCatch({
  if(length(groupIds)<2 || length(groupIds)>3 || length(anchors)!=5 || anyDuplicated(anchors) ||
     any(!anchors %in% colnames(dat)) || nrow(dat)>policy$runtime$maximumRespondents) stop('INVALID_RESEARCH_DESIGN')
  if(identical(input$operation,'BOOTSTRAP_REFIT')) {
    if(!input$bootstrapAnchor %in% anchors) stop('INVALID_BOOTSTRAP_TARGET')
    stage <- 'BOOTSTRAP_TARGET_REFIT'
    bootstrap_model <- fit(setdiff(colnames(dat),input$bootstrapAnchor))
    list(operation='BOOTSTRAP_REFIT',targetAnchor=input$bootstrapAnchor,
         target=model_block(bootstrap_model,input$bootstrapAnchor),
         diagnosticOnly=TRUE,canonicalScoring=FALSE)
  } else {
  stage <- 'JOINT_FIT'
  model <- fit(colnames(dat))
  joint <- model_block(model)
  released <- list(); legacy <- list()
  for(anchor in anchors) {
    stage <- 'ANCHOR_RELEASE'
    release <- tryCatch(fit(setdiff(colnames(dat),anchor)),error=function(e) NULL)
    block <- if(is.null(release)) list(converged=FALSE,atParameterBoundary=FALSE,reason='RELEASE_FIT_UNAVAILABLE') else
      tryCatch(model_block(release,anchor),error=function(e) list(converged=FALSE,atParameterBoundary=FALSE,reason='RELEASE_COVARIANCE_UNAVAILABLE'))
    released[[anchor]] <- block
    legacy[[anchor]] <- list(evaluated=FALSE)
    if(isTRUE(block$converged) && !isTRUE(block$atParameterBoundary)) {
      lr <- tryCatch(anova(model,release),error=function(e) NULL)
      shifted <- lapply(groupIds,function(id) {
        pin <- block$mapping[[id]]
        a <- block$values[pin$a+1L]
        d <- block$values[pin$intercepts+1L]
        list(a=a,steps=-diff(c(0,d))/a)
      })
      base <- shifted[[1]]
      p <- if(!is.null(lr)) tail(lr$p,1) else NA_real_
      legacy[[anchor]] <- list(evaluated=is.finite(p),p=if(is.finite(p)) p else NULL,
        maximumLogSlopeDifference=max(vapply(shifted,function(x) abs(log(x$a/base$a)),0.)),
        maximumStepDifference=max(vapply(shifted,function(x) max(abs(x$steps-base$steps)),0.)))
    }
  }
  rawp <- vapply(legacy,function(x) if(is.null(x$p)) NA_real_ else x$p,0.)
  adjusted <- p.adjust(rawp,'holm')
  for(j in seq_along(legacy)) legacy[[j]]$holmP <- if(is.finite(adjusted[j])) adjusted[j] else NULL
  # Diagnostic refit: not an alternate source of student results or scale linking.
  stage <- 'REFERENCE_DIAGNOSTIC'
  active <- colSums(!is.na(dat[groups==levels(groups)[1],,drop=FALSE]))>0
  original <- tryCatch(mirt(dat[groups==levels(groups)[1],active,drop=FALSE],1,itemtype=types[active],
    method='EM',quadpts=policy$engine$quadrature,TOL=policy$engine$tolerance,SE=TRUE,SE.type='Oakes',
    verbose=FALSE,technical=list(NCYCLES=policy$engine$maxIterations)),error=function(e) NULL)
  reference <- if(is.null(original)) list(converged=FALSE,diagnosticOnly=TRUE) else
    tryCatch(c(model_block(original,original_only=TRUE),list(diagnosticOnly=TRUE)),
             error=function(e) list(converged=FALSE,diagnosticOnly=TRUE))
  list(converged=joint$converged,atParameterBoundary=joint$atParameterBoundary,joint=joint,
       released=released,anchors=legacy,referenceRefit=reference,
       engine=list(R=as.character(getRversion()),mirt=as.character(packageVersion('mirt'))))
  }
},error=function(e) list(converged=FALSE,atParameterBoundary=FALSE,engineStage=stage,
                         failureCode='SCIENTIFIC_OUTPUT_UNAVAILABLE'))
write_json(result,args[2],auto_unbox=TRUE,null='null',na='null',digits=16)
