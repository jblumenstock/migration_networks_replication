library(fixest)


# ################### Disaggregating the friend of friend effect by the strength of the 2nd-degree tie ########################

da = read.csv("data/dest_home_d_s_l_infor_strong.csv")

da$dest_is_home = 1
da$dest_is_home[da$home != da$dest] = 0
da$user_dest <- paste(da$user, da$dest, sep="_")
da$user_degree_dest <- paste(da$user, da$degree_dest, sep="_")
da$home_dest_user <- paste(da$home, da$dest, da$user, sep="_")
da$home_dest_date <- paste(da$home, da$dest, da$date, sep="_")
da$date_user <- paste(da$date, da$user, sep="_")
da$date_dest_dest_is_home <- paste(da$date, da$dest, da$dest_is_home, sep="_")
da$degree_dest_is_home <- paste(da$degree_dest, da$dest_is_home, sep="_")

da$l = da$l / 1000
da$s_s_infor = da$s_s_infor / 1000
da$s_w_infor = da$s_w_infor / 1000
da$w_s_infor = da$w_s_infor / 1000
da$w_w_infor = da$w_w_infor / 1000

model_1 <- feglm(if_move ~ l + l:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_1, cluster=~user)


model_1_vcov = vcov(model_1, cluster=~user)
model_1_se_home = c()
a <- rep(0, 2)
a[1] <- 1
a[2] <- 1
se = c(sqrt(t(a) %*% model_1_vcov %*% a))
model_1_se_home = append(model_1_se_home, se)


model_1_coef_home = c(
    coefficients(model_1)[1] + coefficients(model_1)[2]
)

summary(model_1, cluster=~user)
model_1_coef_home
model_1_se_home
pnorm(-abs(model_1_coef_home) / model_1_se_home)



model_2 <- feglm(if_move ~ s_s_infor + s_s_infor:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_2, cluster=~user)

model_2_vcov = vcov(model_2, cluster=~user)
model_2_se_home = c()
a <- rep(0, 2)
a[1] <- 1
a[2] <- 1
se = c(sqrt(t(a) %*% model_2_vcov %*% a))
model_2_se_home = append(model_2_se_home, se)

model_2_coef_home = c(
    coefficients(model_2)[1] + coefficients(model_2)[2]
)

summary(model_2, cluster=~user)
model_2_coef_home
model_2_se_home
pnorm(-abs(model_2_coef_home) / model_2_se_home)



model_3 <- feglm(if_move ~ s_w_infor + s_w_infor:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_3, cluster=~user)

model_3_vcov = vcov(model_3, cluster=~user)
model_3_se_home = c()
a <- rep(0, 2)
a[1] <- 1
a[2] <- 1
se = c(sqrt(t(a) %*% model_3_vcov %*% a))
model_3_se_home = append(model_3_se_home, se)

model_3_coef_home = c(
    coefficients(model_3)[1] + coefficients(model_3)[2]
)

summary(model_3, cluster=~user)
model_3_coef_home
model_3_se_home
pnorm(-abs(model_3_coef_home) / model_3_se_home)



model_4 <- feglm(if_move ~ w_s_infor + w_s_infor:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_4, cluster=~user)

model_4_vcov = vcov(model_4, cluster=~user)
model_4_se_home = c()
a <- rep(0, 2)
a[1] <- 1
a[2] <- 1
se = c(sqrt(t(a) %*% model_4_vcov %*% a))
model_4_se_home = append(model_4_se_home, se)

model_4_coef_home = c(
    coefficients(model_4)[1] + coefficients(model_4)[2]
)

summary(model_4, cluster=~user)
model_4_coef_home
model_4_se_home
pnorm(-abs(model_4_coef_home) / model_4_se_home)



model_5 <- feglm(if_move ~ w_w_infor + w_w_infor:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_5, cluster=~user)

model_5_vcov = vcov(model_5, cluster=~user)
model_5_se_home = c()
a <- rep(0, 2)
a[1] <- 1
a[2] <- 1
se = c(sqrt(t(a) %*% model_5_vcov %*% a))
model_5_se_home = append(model_5_se_home, se)

model_5_coef_home = c(
    coefficients(model_5)[1] + coefficients(model_5)[2]
)

summary(model_5, cluster=~user)
model_5_coef_home
model_5_se_home
pnorm(-abs(model_5_coef_home) / model_5_se_home)




model_6 <- feglm(if_move ~ s_s_infor + s_s_infor:dest_is_home + s_w_infor + s_w_infor:dest_is_home + w_s_infor + w_s_infor:dest_is_home + w_w_infor + w_w_infor:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_6, cluster=~user)

model_6_vcov = vcov(model_6, cluster=~user)
model_6_se_home = c()
a <- rep(0, 8)
a[1] <- 1
a[5] <- 1
se = c(sqrt(t(a) %*% model_6_vcov %*% a))
model_6_se_home = append(model_6_se_home, se)

a <- rep(0, 8)
a[2] <- 1
a[6] <- 1
se = c(sqrt(t(a) %*% model_6_vcov %*% a))
model_6_se_home = append(model_6_se_home, se)

a <- rep(0, 8)
a[3] <- 1
a[7] <- 1
se = c(sqrt(t(a) %*% model_6_vcov %*% a))
model_6_se_home = append(model_6_se_home, se)

a <- rep(0, 8)
a[4] <- 1
a[8] <- 1
se = c(sqrt(t(a) %*% model_6_vcov %*% a))
model_6_se_home = append(model_6_se_home, se)

model_6_coef_home = c(
    coefficients(model_6)[1] + coefficients(model_6)[5], 
    coefficients(model_6)[2] + coefficients(model_6)[6], 
    coefficients(model_6)[3] + coefficients(model_6)[7],
    coefficients(model_6)[4] + coefficients(model_6)[8]
)

summary(model_6, cluster=~user)
model_6_coef_home
model_6_se_home
pnorm(-abs(model_6_coef_home) / model_6_se_home)
