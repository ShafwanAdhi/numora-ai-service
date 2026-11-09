lock <- read.delim('/opt/irt/r-sources.lock.tsv', stringsAsFactors=FALSE)
repo <- tempfile('locked-cran-')
dir.create(file.path(repo,'src','contrib'), recursive=TRUE)
for (i in seq_len(nrow(lock))) {
  file <- file.path(repo,'src','contrib',paste0(lock$name[i],'_',lock$version[i],'.tar.gz'))
  download.file(lock$url[i],file,quiet=TRUE,method='libcurl')
  actual <- strsplit(system2('sha256sum',file,stdout=TRUE),' ')[[1]][1]
  stopifnot(identical(actual,lock$sha256[i]))
}
tools::write_PACKAGES(file.path(repo,'src','contrib'),type='source')
install.packages(c('mirt','jsonlite'), repos=paste0('file://',repo), type='source',
                 dependencies=c('Depends','Imports','LinkingTo'), Ncpus=1)
stopifnot(as.character(packageVersion('mirt'))=='1.48')
for(i in seq_len(nrow(lock))) {
  actual <- packageDescription(lock$name[i],fields='Version')
  if(!identical(actual,lock$version[i])) stop(paste('Locked version mismatch:',lock$name[i],actual,lock$version[i]))
}
unlink(repo,recursive=TRUE)
