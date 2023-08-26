library(fixest)


# ################### The role of recent migrants and co-migrants ########################

da = read.csv("data/dest_home_d_s_l_recent_migrant.csv")

da$dest_is_home = 1
da$dest_is_home[da$home_dest != da$dest_dest] = 0
da$d_dest = da$d_dest/1000
da$l_dest = da$l_dest/1000
da$s_dest = da$s_dest/1000
da$recent_mig_dest = da$recent_mig_dest/1000
da$co_mig_dest = da$co_mig_dest/1000
da$date_user = paste(da$date, da$user, sep="_")
da$date_dest_dest_is_home = paste(da$date, da$dest_dest, da$dest_is_home, sep="_")
da$degree_dest_is_home = paste(da$d_dest, da$dest_is_home, sep="_")


model_recent = feglm(if_move ~ d_dest+d_dest:dest_is_home+s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home+recent_mig_dest+recent_mig_dest:dest_is_home | date_user + date_dest_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_recent, cluster=~user)

model_recent_vcov = vcov(model_recent, cluster=~user)
model_recent_se_home = c()
a = rep(0, 8)
a[1] = 1
a[5] = 1
se = c(sqrt(t(a) %*% model_recent_vcov %*% a))
model_recent_se_home = append(model_recent_se_home, se)

a = rep(0, 8)
a[2] = 1
a[6] = 1
se = c(sqrt(t(a) %*% model_recent_vcov %*% a))
model_recent_se_home = append(model_recent_se_home, se)

a = rep(0, 8)
a[3] = 1
a[7] = 1
se = c(sqrt(t(a) %*% model_recent_vcov %*% a))
model_recent_se_home = append(model_recent_se_home, se)

a = rep(0, 8)
a[4] = 1
a[8] = 1
se = c(sqrt(t(a) %*% model_recent_vcov %*% a))
model_recent_se_home = append(model_recent_se_home, se)

model_recent_coef_home = c(
    coefficients(model_recent)[1] + coefficients(model_recent)[5], 
    coefficients(model_recent)[2] + coefficients(model_recent)[6], 
    coefficients(model_recent)[3] + coefficients(model_recent)[7],
    coefficients(model_recent)[4] + coefficients(model_recent)[8]
)

summary(model_recent, cluster=~user)
model_recent_coef_home
model_recent_se_home
pnorm(-abs(model_recent_coef_home) / model_recent_se_home)



model_co_migrant = feglm(if_move ~ d_dest+d_dest:dest_is_home+s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home+co_mig_dest+co_mig_dest:dest_is_home | date_user + date_dest_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_co_migrant, cluster=~user)

model_co_migrant_vcov = vcov(model_co_migrant, cluster=~user)
model_co_migrant_se_home = c()
a = rep(0, 8)
a[1] = 1
a[5] = 1
se = c(sqrt(t(a) %*% model_co_migrant_vcov %*% a))
model_co_migrant_se_home = append(model_co_migrant_se_home, se)

a = rep(0, 8)
a[2] = 1
a[6] = 1
se = c(sqrt(t(a) %*% model_co_migrant_vcov %*% a))
model_co_migrant_se_home = append(model_co_migrant_se_home, se)

a = rep(0, 8)
a[3] = 1
a[7] = 1
se = c(sqrt(t(a) %*% model_co_migrant_vcov %*% a))
model_co_migrant_se_home = append(model_co_migrant_se_home, se)

a = rep(0, 8)
a[4] = 1
a[8] = 1
se = c(sqrt(t(a) %*% model_co_migrant_vcov %*% a))
model_co_migrant_se_home = append(model_co_migrant_se_home, se)

model_co_migrant_coef_home = c(
    coefficients(model_co_migrant)[1] + coefficients(model_co_migrant)[5], 
    coefficients(model_co_migrant)[2] + coefficients(model_co_migrant)[6], 
    coefficients(model_co_migrant)[3] + coefficients(model_co_migrant)[7],
    coefficients(model_co_migrant)[4] + coefficients(model_co_migrant)[8]
)

summary(model_co_migrant, cluster=~user)
model_co_migrant_coef_home
model_co_migrant_se_home
pnorm(-abs(model_co_migrant_coef_home) / model_co_migrant_se_home)


