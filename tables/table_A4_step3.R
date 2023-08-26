library(fixest)


######################### longterm vs shortterm ###################
da = read.csv("data/dest_home_d_s_l_shorttime_longtime.csv")

da$dest_is_home = 1
da$dest_is_home[da$home != da$dest] = 0
da$d_dest = da$d/1000
da$l_dest = da$l/1000
da$s_dest = da$s/1000
da$date_user = paste(da$date, da$user, sep="_")
da$date_dest_dest_is_home = paste(da$date, da$dest, da$dest_is_home, sep="_")
da$degree_dest_is_home = paste(da$d_dest, da$dest_is_home, sep="_")

da_longterm = da[da$permanent==1,]
da_shortterm = da[da$temporary==1,]

da_raw = read.csv("data/dest_home_d_s_l.csv")

da_raw$dest_is_home = 1
da_raw$dest_is_home[da_raw$home_dest != da_raw$dest_dest] = 0
da_raw$d_dest = da_raw$d_dest/1000
da_raw$l_dest = da_raw$l_dest/1000
da_raw$s_dest = da_raw$s_dest/1000
da_raw$date_user = paste(da_raw$date, da_raw$user, sep="_")
da_raw$date_dest_dest_is_home = paste(da_raw$date, da_raw$dest_dest, da_raw$dest_is_home, sep="_")
da_raw$degree_dest_is_home = paste(da_raw$d_dest, da_raw$dest_is_home, sep="_")

non_migrant = da_raw[(da_raw$if_move==1) & (da_raw$home_dest == da_raw$dest_dest),]
non_migrant_unique = unique(non_migrant[c("user", "date")])
non_migrant_df = merge(x=da_raw,y=non_migrant_unique,by=c("user", "date"))

variables = c('if_move', 'user', 's_dest', 'l_dest', 'dest_is_home', 'date_user', 'date_dest_dest_is_home', 'degree_dest_is_home')

da_longterm_v1 = rbind(da_longterm[variables], non_migrant_df[variables])
da_shortterm_v1 = rbind(da_shortterm[variables], non_migrant_df[variables])

# longterm
model_longterm = feglm(if_move ~ s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da_longterm_v1, vcov = ~user, family = binomial("logit"))
summary(model_longterm, cluster=~user)

model_longterm_vcov = vcov(model_longterm, cluster=~user)
model_longterm_se_home = c()
a = rep(0, 4)
a[1] = 1
a[3] = 1
se = c(sqrt(t(a) %*% model_longterm_vcov %*% a))
model_longterm_se_home = append(model_longterm_se_home, se)

a = rep(0, 4)
a[2] = 1
a[4] = 1
se = c(sqrt(t(a) %*% model_longterm_vcov %*% a))
model_longterm_se_home = append(model_longterm_se_home, se)

model_longterm_coef_home = c(
    coefficients(model_longterm)[1] + coefficients(model_longterm)[3], 
    coefficients(model_longterm)[2] + coefficients(model_longterm)[4]
)

summary(model_longterm, cluster=~user)
model_longterm_coef_home
model_longterm_se_home
pnorm(-abs(model_longterm_coef_home) / model_longterm_se_home)


# shortterm
model_shortterm = feglm(if_move ~ s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da_shortterm_v1, vcov = ~user, family = binomial("logit"))
summary(model_shortterm, cluster=~user)

model_shortterm_vcov = vcov(model_shortterm, cluster=~user)
model_shortterm_se_home = c()
a = rep(0, 4)
a[1] = 1
a[3] = 1
se = c(sqrt(t(a) %*% model_shortterm_vcov %*% a))
model_shortterm_se_home = append(model_shortterm_se_home, se)

a = rep(0, 4)
a[2] = 1
a[4] = 1
se = c(sqrt(t(a) %*% model_shortterm_vcov %*% a))
model_shortterm_se_home = append(model_shortterm_se_home, se)

model_shortterm_coef_home = c(
    coefficients(model_shortterm)[1] + coefficients(model_shortterm)[3], 
    coefficients(model_shortterm)[2] + coefficients(model_shortterm)[4]
)

summary(model_shortterm, cluster=~user)
model_shortterm_coef_home
model_shortterm_se_home
pnorm(-abs(model_shortterm_coef_home) / model_shortterm_se_home)

