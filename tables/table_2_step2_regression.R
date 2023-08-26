library(fixest)

# read and process data
da = read.csv("data/dest_home_d_s_l.csv")
da$dest_is_home = 1
da$dest_is_home[da$home_dest != da$dest_dest] = 0.
da$d_dest = da$d_dest/1000
da$l_dest = da$l_dest/1000
da$s_dest = da$s_dest/1000
da$date_user <- paste(da$date, da$user, sep="_")
da$date_dest_dest_is_home <- paste(da$date, da$dest_dest, da$dest_is_home, sep="_")
da$degree_dest_is_home <- paste(da$d_dest, da$dest_is_home, sep="_")


############### model 1 ###############

model_1 <- feglm(if_move ~ d_dest*dest_is_home+s_dest*dest_is_home+l_dest*dest_is_home | date_user, da, vcov = ~user, family = binomial("logit"))

# calculate the home s.e.
model_1_vcov = vcov(model_1, cluster=~user)
model_1_se_home = c()
a <- rep(0, 7)
a[1] <- 1
a[5] <- 1
se = c(sqrt(t(a) %*% model_1_vcov %*% a))
model_1_se_home = append(model_1_se_home, se)

a <- rep(0, 7)
a[3] <- 1
a[6] <- 1
se = c(sqrt(t(a) %*% model_1_vcov %*% a))
model_1_se_home = append(model_1_se_home, se)

a <- rep(0, 7)
a[4] <- 1
a[7] <- 1
se = c(sqrt(t(a) %*% model_1_vcov %*% a))
model_1_se_home = append(model_1_se_home, se)

# calculate the home coefficient
model_1_coef_home = c(
    coefficients(model_1)[1] + coefficients(model_1)[5], 
    coefficients(model_1)[3] + coefficients(model_1)[6],
    coefficients(model_1)[4] + coefficients(model_1)[7]
)

summary(model_1, cluster=~user)
# home coefficient
model_1_coef_home
# home s.e.
model_1_se_home
# calculate the home p value
# reference: https://stats.stackexchange.com/questions/237073/how-does-r-calculate-the-p-value-for-this-binomial-regression
# confirmed based on the p value of variables in the regression result
pnorm(-abs(model_1_coef_home) / model_1_se_home)


############### model 2 ###############

model_2 <- feglm(if_move ~ d_dest+d_dest:dest_is_home+s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home | date_user + date_dest_dest_is_home, da, vcov = ~user, family = binomial("logit"))

model_2_vcov = vcov(model_2, cluster=~user)
model_2_se_home = c()
a <- rep(0, 6)
a[1] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% model_2_vcov %*% a))
model_2_se_home = append(model_2_se_home, se)

a <- rep(0, 6)
a[2] <- 1
a[5] <- 1
se = c(sqrt(t(a) %*% model_2_vcov %*% a))
model_2_se_home = append(model_2_se_home, se)

a <- rep(0, 6)
a[3] <- 1
a[6] <- 1
se = c(sqrt(t(a) %*% model_2_vcov %*% a))
model_2_se_home = append(model_2_se_home, se)

model_2_coef_home = c(
    coefficients(model_2)[1] + coefficients(model_2)[4], 
    coefficients(model_2)[2] + coefficients(model_2)[5],
    coefficients(model_2)[3] + coefficients(model_2)[6]
)

summary(model_2, cluster=~user)
model_2_coef_home
model_2_se_home
pnorm(-abs(model_2_coef_home) / mod2_se_home)


############### model 3 ###############

model_3 <- feglm(if_move ~ s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))

model_3_vcov = vcov(model_3, cluster=~user)
model_3_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% model_3_vcov %*% a))
model_3_se_home = append(model_3_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% model_3_vcov %*% a))
model_3_se_home = append(model_3_se_home, se)

model_3_coef_home = c(
    coefficients(model_3)[1] + coefficients(model_3)[3], 
    coefficients(model_3)[2] + coefficients(model_3)[4]
)

summary(model_3, cluster=~user)
model_3_coef_home
model_3_se_home
pnorm(-abs(model_3_coef_home) / model_3_se_home)
