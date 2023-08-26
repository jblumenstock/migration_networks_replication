library(fixest)


# ################### Beyond location-specific subnetworks ###################

da = read.csv("data/dest_home_d_s_l_information_overall_network.csv")

da$dest_is_home = 1
da$dest_is_home[da$home != da$dest] = 0
da$d_dest = da$d_dest/1000
da$d_home = da$d_home/1000
da$d_all = da$d_all/1000
da$information_dest_case_1 = da$information_dest_case_1/1000
da$information_dest_case_2 = da$information_dest_case_2/1000
da$information_dest_case_3 = da$information_dest_case_3/1000
da$information_home_case_1 = da$information_home_case_1/1000
da$information_home_case_2 = da$information_home_case_2/1000
da$information_home_case_3 = da$information_home_case_3/1000
da$support_dest_case_1 = da$support_dest_case_1/1000
da$support_dest_case_2 = da$support_dest_case_2/1000
da$support_dest_case_3 = da$support_dest_case_3/1000
da$support_home_case_1 = da$support_home_case_1/1000
da$support_home_case_2 = da$support_home_case_2/1000
da$support_home_case_3 = da$support_home_case_3/1000

da$information_dest_case_2_only = da$information_dest_case_2_only/1000
da$information_dest_case_3_only = da$information_dest_case_3_only/1000
da$information_home_case_2_only = da$information_home_case_2_only/1000
da$information_home_case_3_only = da$information_home_case_3_only/1000
da$support_dest_case_2_only = da$support_dest_case_2_only/1000
da$support_dest_case_3_only = da$support_dest_case_3_only/1000
da$support_home_case_2_only = da$support_home_case_2_only/1000
da$support_home_case_3_only = da$support_home_case_3_only/1000


da$degree_other = ifelse(da$home != da$dest, da$d_all - da$d_home - da$d_dest, da$d_all - da$d_home)

da$date_user <- paste(da$date, da$user, sep="_")
da$date_dest_dest_is_home <- paste(da$date, da$dest, da$dest_is_home, sep="_")
da$degree_dest_is_home <- paste(da$d_dest, da$dest_is_home, sep="_")
da$degree_other_dest_is_home <- paste(da$degree_other, da$dest_is_home, sep="_")

############### model 1 ###############

model_1 <- feglm(if_move ~ information_dest_case_1+information_dest_case_1:dest_is_home+support_dest_case_1+support_dest_case_1:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_1, cluster=~user)

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


############### model 2 ###############

model_2 <- feglm(if_move ~ information_dest_case_2_only+information_dest_case_2_only:dest_is_home+support_dest_case_2_only+support_dest_case_2_only:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_2, cluster=~user)

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