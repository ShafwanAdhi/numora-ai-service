suppressPackageStartupMessages(library(mirt))
suppressPackageStartupMessages(library(jsonlite))
set.seed(20261109)
types <- c('2PL','gpcm',rep('2PL',28))
dat <- matrix(sample(0:1,3000,replace=TRUE),100,30)
dat[,2] <- sample(0:2,100,replace=TRUE)
colnames(dat) <- paste0('q',1:30)
pars <- mirt(dat,1,itemtype=types,pars='values',verbose=FALSE)
for(j in 1:30) {
  pars$value[pars$item==colnames(dat)[j] & pars$name=='a1'] <- 1.3
  pars$value[pars$item==colnames(dat)[j] & pars$name=='d'] <- -.52
}
# Unordered absolute GPCM steps: 0.8, -0.6; internal cumulative d: -1.04,-0.26.
pars$value[pars$item=='q2' & pars$name=='d1'] <- -1.04
pars$value[pars$item=='q2' & pars$name=='d2'] <- -.26
pars$est <- FALSE
model <- mirt(dat,1,itemtype=types,pars=pars,verbose=FALSE)
items <- lapply(1:30,function(j) extract.item(model,j))
grids <- lapply(items[1:2],function(item) lapply(-4:4,function(theta) I(as.numeric(probtrace(item,matrix(theta))))))
patterns <- list(rep(0,30),c(1,2,rep(1,28)),c(1,1,rep(c(0,1),14)))
posteriors <- lapply(patterns,function(pattern) {
  density <- function(theta) vapply(theta,function(t) {
    p <- vapply(1:30,function(j) probtrace(items[[j]],matrix(t))[1,pattern[j]+1],0.0)
    exp(sum(log(p))+dnorm(t,log=TRUE))
  },0.0)
  total <- integrate(density,-10,10,rel.tol=1e-10,abs.tol=1e-30,subdivisions=1000)$value
  mean <- integrate(function(t) t*density(t),-10,10,rel.tol=1e-10,abs.tol=1e-30,subdivisions=1000)$value/total
  variance <- integrate(function(t) (t-mean)^2*density(t),-10,10,rel.tol=1e-10,abs.tol=1e-30,subdivisions=1000)$value/total
  expected <- sum(vapply(items,function(item) {
    p <- as.numeric(probtrace(item,matrix(mean)))
    sum((seq_along(p)-1)*p)/(length(p)-1)
  },0.0))/30*100
  list(theta=mean,sd=sqrt(variance),unroundedScore=expected)
})
write_json(list(probabilities=grids,posteriors=posteriors),commandArgs(TRUE)[1],auto_unbox=TRUE,digits=16)
