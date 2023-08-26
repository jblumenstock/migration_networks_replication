library(fixest)

######################### first_time vs repeat ###################
da = read.csv("dest_home_d_s_l_firsttime_repeat.csv")

da$dest_is_home = 1
da$dest_is_home[da$home_dest != da$dest_dest] = 0
da$d_dest = da$d_dest/1000
da$l_dest = da$l_dest/1000
da$s_dest = da$s_dest/1000
da$date_user <- paste(da$date, da$user, sep="_")
da$date_dest_dest_is_home <- paste(da$date, da$dest_dest, da$dest_is_home, sep="_")
da$degree_dest_is_home <- paste(da$d_dest, da$dest_is_home, sep="_")

da_firsttime = da[(da$if_repeat==0) | (da$home_dest==da$dest_dest),]
da_repeat = da[(da$if_repeat==1) | (da$home_dest==da$dest_dest),]

# firsttime
model_fixest_firsttime <- feglm(if_move ~ s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da_firsttime, vcov = ~user, family = binomial("logit"))
summary(model_fixest_firsttime, cluster=~user)

mod3_vcov = vcov(model_fixest_firsttime, cluster=~user)
mod3_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% mod3_vcov %*% a))
mod3_se_home = append(mod3_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% mod3_vcov %*% a))
mod3_se_home = append(mod3_se_home, se)

mod3_coef_home = c(
    coefficients(model_fixest_firsttime)[1] + coefficients(model_fixest_firsttime)[3], 
    coefficients(model_fixest_firsttime)[2] + coefficients(model_fixest_firsttime)[4]
)

summary(model_fixest_firsttime, cluster=~user)
mod3_coef_home
mod3_se_home
pnorm(-abs(mod3_coef_home) / mod3_se_home)


# repeat
model_fixest_repeat <- feglm(if_move ~ s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da_repeat, vcov = ~user, family = binomial("logit"))
summary(model_fixest_repeat, cluster=~user)

mod3_vcov = vcov(model_fixest_repeat, cluster=~user)
mod3_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% mod3_vcov %*% a))
mod3_se_home = append(mod3_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% mod3_vcov %*% a))
mod3_se_home = append(mod3_se_home, se)

mod3_coef_home = c(
    coefficients(model_fixest_repeat)[1] + coefficients(model_fixest_repeat)[3], 
    coefficients(model_fixest_repeat)[2] + coefficients(model_fixest_repeat)[4]
)

summary(model_fixest_repeat, cluster=~user)
mod3_coef_home
mod3_se_home
pnorm(-abs(mod3_coef_home) / mod3_se_home)
