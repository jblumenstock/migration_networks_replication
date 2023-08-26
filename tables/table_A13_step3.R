library(fixest)

da = read.csv('data/dest_home_for_regression_information_support_diff_between_-6_to_-2_month.csv')
da$dest_is_home = 1
da$dest_is_home[da$home_dest != da$dest_dest] = 0
da$user_dest <- paste(da$user, da$dest_dest, sep="_")
da$user_degree_dest <- paste(da$user, da$degree_dest, sep="_")
da$home_dest_user <- paste(da$home_dest, da$dest_dest, da$user, sep="_")
da$home_dest_date <- paste(da$home_dest, da$dest_dest, da$date, sep="_")
da$if_move = da$if_move_x

d1 = da
d1$information_diff_dest = d1$information_diff_dest/1000
d1$support_diff_dest = d1$support_diff_dest/1000
d1$degree_dest = d1$degree_dest/1000
d1$information_diff_home = d1$information_diff_home/1000
d1$support_diff_home = d1$support_diff_home/1000
d1$degree_home = d1$degree_home/1000
d1$date_dest_dest_is_home <- paste(d1$date, d1$dest_dest, d1$dest_is_home, sep="_")
d1$degree_dest_is_home <- paste(d1$degree_dest, d1$dest_is_home, sep="_")
d1$date_user <- paste(d1$date, d1$user, sep="_")


# Model 1
model_1 <- feglm(if_move ~ information_diff_dest+information_diff_dest:dest_is_home+support_diff_dest+support_diff_dest:dest_is_home | date_user + date_dest_dest_is_home, d1, vcov = ~user, family = binomial("logit"))
summary(model_1, cluster=~user)

r = model_1$residuals
sse = sum(r ^ 2)
model_0 <- feglm(if_move ~ 1 | date_user + date_dest_dest_is_home, d1, vcov = ~user, family = binomial("logit"))
model_0_summary = summary(model_0, cluster=~user)
r_0 = model_0_summary$residuals
sse_0 = sum(r_0 ^ 2)
partial_dest_model_1 = 1 - sse / sse_0

model_1_vcov = vcov(model_1, cluster=~user)
model_1_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% model_1_vcov %*% a))
model_1_se_home = append(model_1_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% model_1_vcov %*% a))
model_1_se_home = append(model_1_se_home, se)

model_1_coef_home = c(
    coefficients(model_1)[1] + coefficients(model_1)[3], 
    coefficients(model_1)[2] + coefficients(model_1)[4]
)

summary(model_1, cluster=~user)
model_1_coef_home
model_1_se_home
pnorm(-abs(model_1_coef_home) / model_1_se_home)


# model 2
da = read.csv('data/dest_home_for_regression_information_support_diff_between_-12_to_-2_month.csv')
da$dest_is_home = 1
da$dest_is_home[da$home_dest != da$dest_dest] = 0
da$user_dest <- paste(da$user, da$dest_dest, sep="_")
da$user_degree_dest <- paste(da$user, da$degree_dest, sep="_")
da$home_dest_user <- paste(da$home_dest, da$dest_dest, da$user, sep="_")
da$home_dest_date <- paste(da$home_dest, da$dest_dest, da$date, sep="_")
da$if_move = da$if_move_x

d1 = da
d1$information_diff_dest = d1$information_diff_dest/1000
d1$support_diff_dest = d1$support_diff_dest/1000
d1$degree_dest = d1$degree_dest/1000
d1$information_diff_home = d1$information_diff_home/1000
d1$support_diff_home = d1$support_diff_home/1000
d1$degree_home = d1$degree_home/1000
d1$date_dest_dest_is_home <- paste(d1$date, d1$dest_dest, d1$dest_is_home, sep="_")
d1$degree_dest_is_home <- paste(d1$degree_dest, d1$dest_is_home, sep="_")
d1$date_user <- paste(d1$date, d1$user, sep="_")


model_2 <- feglm(if_move ~ information_diff_dest+information_diff_dest:dest_is_home+support_diff_dest+support_diff_dest:dest_is_home | date_user + date_dest_dest_is_home, d1, vcov = ~user, family = binomial("logit"))
summary(model_2, cluster=~user)

r = model_2$residuals
sse = sum(r ^ 2)
model_0 <- feglm(if_move ~ 1 | date_user + date_dest_dest_is_home, d1, vcov = ~user, family = binomial("logit"))
model_0_summary = summary(model_0, cluster=~user)
r_0 = model_0_summary$residuals
sse_0 = sum(r_0 ^ 2)
partial_dest_model_2 = 1 - sse / sse_0



model_2_vcov = vcov(model_2, cluster=~user)
model_2_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% model_2_vcov %*% a))
model_2_se_home = append(model_2_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% model_2_vcov %*% a))
model_2_se_home = append(model_2_se_home, se)

model_2_coef_home = c(
    coefficients(model_2)[1] + coefficients(model_2)[3], 
    coefficients(model_2)[2] + coefficients(model_2)[4]
)

summary(model_2, cluster=~user)
model_2_coef_home
model_2_se_home
pnorm(-abs(model_2_coef_home) / model_2_se_home)

