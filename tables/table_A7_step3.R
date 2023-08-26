library(fixest)


# ################### visit before migration ########################

da = read.csv("data/dest_home_d_s_l_visit_before.csv")

da$dest_is_home = 1
da$dest_is_home[da$home_dest != da$dest_dest] = 0
da$d_dest = da$d_dest/1000
da$l_dest = da$l_dest/1000
da$s_dest = da$s_dest/1000
da$date_user <- paste(da$date, da$user, sep="_")
da$date_dest_dest_is_home <- paste(da$date, da$dest_dest, da$dest_is_home, sep="_")
da$degree_dest_is_home <- paste(da$d_dest, da$dest_is_home, sep="_")

da$if_visit[which(da$if_visit > 0)] = 0.001
da$if_visit_night[which(da$if_visit_night > 0)] = 0.001


model <- feglm(if_move ~ d_dest+d_dest:dest_is_home+s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home | date_user + date_dest_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model, cluster=~user)

model_vcov = vcov(model, cluster=~user)
model_se_home = c()
a <- rep(0, 6)
a[1] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% model_vcov %*% a))
model_se_home = append(model_se_home, se)

a <- rep(0, 6)
a[2] <- 1
a[5] <- 1
se = c(sqrt(t(a) %*% model_vcov %*% a))
model_se_home = append(model_se_home, se)

a <- rep(0, 6)
a[3] <- 1
a[6] <- 1
se = c(sqrt(t(a) %*% model_vcov %*% a))
model_se_home = append(model_se_home, se)

model_coef_home = c(
    coefficients(model)[1] + coefficients(model)[4], 
    coefficients(model)[2] + coefficients(model)[5], 
    coefficients(model)[3] + coefficients(model)[6]
)

summary(model, cluster=~user)
model_coef_home
model_se_home
pnorm(-abs(model_coef_home) / model_se_home)



# if_visit
model_visit <- feglm(if_move ~ d_dest+d_dest:dest_is_home+s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home+if_visit | date_user + date_dest_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_visit, cluster=~user)

model_visit_vcov = vcov(model_visit, cluster=~user)
model_visit_se_home = c()
a <- rep(0, 7)
a[1] <- 1
a[5] <- 1
se = c(sqrt(t(a) %*% model_visit_vcov %*% a))
model_visit_se_home = append(model_visit_se_home, se)

a <- rep(0, 7)
a[2] <- 1
a[6] <- 1
se = c(sqrt(t(a) %*% model_visit_vcov %*% a))
model_visit_se_home = append(model_visit_se_home, se)

a <- rep(0, 7)
a[3] <- 1
a[7] <- 1
se = c(sqrt(t(a) %*% model_visit_vcov %*% a))
model_visit_se_home = append(model_visit_se_home, se)

model_visit_coef_home = c(
    coefficients(model_visit)[1] + coefficients(model_visit)[5], 
    coefficients(model_visit)[2] + coefficients(model_visit)[6], 
    coefficients(model_visit)[3] + coefficients(model_visit)[7]
)

summary(model_visit, cluster=~user)
model_visit_coef_home
model_visit_se_home
pnorm(-abs(model_visit_coef_home) / model_visit_se_home)


# visit_night
model_visit_night <- feglm(if_move ~ d_dest+d_dest:dest_is_home+s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home+if_visit_night | date_user + date_dest_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_visit_night, cluster=~user)

model_visit_night_vcov = vcov(model_visit_night, cluster=~user)
model_visit_night_se_home = c()
a <- rep(0, 7)
a[1] <- 1
a[5] <- 1
se = c(sqrt(t(a) %*% model_visit_night_vcov %*% a))
model_visit_night_se_home = append(model_visit_night_se_home, se)

a <- rep(0, 7)
a[2] <- 1
a[6] <- 1
se = c(sqrt(t(a) %*% model_visit_night_vcov %*% a))
model_visit_night_se_home = append(model_visit_night_se_home, se)

a <- rep(0, 7)
a[3] <- 1
a[7] <- 1
se = c(sqrt(t(a) %*% model_visit_night_vcov %*% a))
model_visit_night_se_home = append(model_visit_night_se_home, se)

model_visit_night_coef_home = c(
    coefficients(model_visit_night)[1] + coefficients(model_visit_night)[5], 
    coefficients(model_visit_night)[2] + coefficients(model_visit_night)[6], 
    coefficients(model_visit_night)[3] + coefficients(model_visit_night)[7]
)

summary(model_visit_night, cluster=~user)
model_visit_night_coef_home
model_visit_night_se_home
pnorm(-abs(model_visit_night_coef_home) / model_visit_night_se_home)

