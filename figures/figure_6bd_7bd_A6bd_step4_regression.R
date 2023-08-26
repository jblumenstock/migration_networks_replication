library(fixest)

################## support #################

dta_support_dest_nonorm = read.csv(paste('data/support_dest_for_regression_22degree_sampled_10pct.csv', sep=""))
dta_support_dest_nonorm = dta_support_dest_nonorm[dta_support_dest_nonorm$d < 23,]
dta_support_dest_nonorm$home_dest_date <- paste(dta_support_dest_nonorm$home, dta_support_dest_nonorm$dest, dta_support_dest_nonorm$date, sep="_")
da = dta_support_dest_nonorm

da$dest_is_home = 1
da$dest_is_home[da$home != da$dest] = 0
da$support.2 = da$support.2 / 1000
da$support.3 = da$support.3 / 1000
da$support.4 = da$support.4 / 1000
da$support.5 = da$support.5 / 1000
da$support.6 = da$support.6 / 1000
da$support.7 = da$support.7 / 1000
da$support.8 = da$support.8 / 1000
da$support.9 = da$support.9 / 1000
da$support.10 = da$support.10 / 1000
da$support.11 = da$support.11 / 1000
da$support.12 = da$support.12 / 1000
da$support.13 = da$support.13 / 1000
da$support.14 = da$support.14 / 1000
da$support.15 = da$support.15 / 1000
da$support.16 = da$support.16 / 1000
da$support.17 = da$support.17 / 1000
da$support.18 = da$support.18 / 1000
da$support.19 = da$support.19 / 1000
da$support.20 = da$support.20 / 1000
da$support.21 = da$support.21 / 1000
da$support.22 = da$support.22 / 1000

da$date_user <- paste(da$date, da$user, sep="_")
da$date_dest_dest_is_home <- paste(da$date, da$dest, da$dest_is_home, sep="_")
da$degree_dest_is_home <- paste(da$d, da$dest_is_home, sep="_")

model1 <- feglm(if_move ~ support.2+support.2:dest_is_home+support.3+support.3:dest_is_home+support.4+support.4:dest_is_home+support.5+support.5:dest_is_home+support.6+support.6:dest_is_home+support.7+support.7:dest_is_home+support.8+support.8:dest_is_home+support.9+support.9:dest_is_home+support.10+support.10:dest_is_home+support.11+support.11:dest_is_home+support.12+support.12:dest_is_home+support.13+support.13:dest_is_home+support.14+support.14:dest_is_home+support.15+support.15:dest_is_home+support.16+support.16:dest_is_home+support.17+support.17:dest_is_home+support.18+support.18:dest_is_home+support.19+support.19:dest_is_home+support.20+support.20:dest_is_home+support.21+support.21:dest_is_home+support.22+support.22:dest_is_home| date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model1, cluster=~user)

vcov = vcov(model1, cluster=~user)

se_home = c()
for (i in 1:21) {
    a <- rep(0, 42)
    a[i] <- 1
    a[i+21] <- 1
    se = c(sqrt(t(a) %*% vcov %*% a))
    se_home = append(se_home, se)
    print(se)
}


coef_home = c()
for (i in 1:21) {
    coef_home = append(coef_home, coefficients(model1)[i] + coefficients(model1)[i+21])
}


conf_int_home_left = coef_home - 1.96 * se_home
conf_int_home_right = coef_home + 1.96 * se_home

conf_int_dest_left = coefficients(model1)[1:21] - 1.96 * summary(model1, cluster=~user)$se[1:21]
conf_int_dest_right = coefficients(model1)[1:21] + 1.96 * summary(model1, cluster=~user)$se[1:21]

write.csv(coef_home, 'data/inset_support_coef_home.csv')
write.csv(coefficients(model1)[1:21], 'data/inset_support_coef_dest.csv')

write.csv(conf_int_home_left, 'data/inset_support_se_home_left.csv')
write.csv(conf_int_home_right, 'data/inset_support_se_home_right.csv')

write.csv(conf_int_dest_left, 'data/inset_support_se_dest_left.csv')
write.csv(conf_int_dest_right, 'data/inset_support_se_dest_right.csv')


################## information #################

dta_information_dest_nonorm = read.csv(paste('data/information_dest_for_regression_22degree_sampled_10pct.csv', sep=""))
dta_information_dest_nonorm = dta_information_dest_nonorm[dta_information_dest_nonorm$d < 23,]
dta_information_dest_nonorm$home_dest_date <- paste(dta_information_dest_nonorm$home, dta_information_dest_nonorm$dest, dta_information_dest_nonorm$date, sep="_")
da = dta_information_dest_nonorm

da$dest_is_home = 1
da$dest_is_home[da$home != da$dest] = 0
da$information.1 = da$information.1 / 1000
da$information.2 = da$information.2 / 1000
da$information.3 = da$information.3 / 1000
da$information.4 = da$information.4 / 1000
da$information.5 = da$information.5 / 1000
da$information.6 = da$information.6 / 1000
da$information.7 = da$information.7 / 1000
da$information.8 = da$information.8 / 1000
da$information.9 = da$information.9 / 1000
da$information.10 = da$information.10 / 1000
da$information.11 = da$information.11 / 1000
da$information.12 = da$information.12 / 1000
da$information.13 = da$information.13 / 1000
da$information.14 = da$information.14 / 1000
da$information.15 = da$information.15 / 1000
da$information.16 = da$information.16 / 1000
da$information.17 = da$information.17 / 1000
da$information.18 = da$information.18 / 1000
da$information.19 = da$information.19 / 1000
da$information.20 = da$information.20 / 1000
da$information.21 = da$information.21 / 1000
da$information.22 = da$information.22 / 1000
da$date_user <- paste(da$date, da$user, sep="_")
da$date_dest_dest_is_home <- paste(da$date, da$dest, da$dest_is_home, sep="_")
da$degree_dest_is_home <- paste(da$d, da$dest_is_home, sep="_")

model <- feglm(if_move ~ information.1+information.1:dest_is_home+information.2+information.2:dest_is_home+information.3+information.3:dest_is_home+information.4+information.4:dest_is_home+information.5+information.5:dest_is_home+information.6+information.6:dest_is_home+information.7+information.7:dest_is_home+information.8+information.8:dest_is_home+information.9+information.9:dest_is_home+information.10+information.10:dest_is_home+information.11+information.11:dest_is_home+information.12+information.12:dest_is_home+information.13+information.13:dest_is_home+information.14+information.14:dest_is_home+information.15+information.15:dest_is_home+information.16+information.16:dest_is_home+information.17+information.17:dest_is_home+information.18+information.18:dest_is_home+information.19+information.19:dest_is_home+information.20+information.20:dest_is_home+information.21+information.21:dest_is_home+information.22+information.22:dest_is_home| date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model, cluster=~user)

vcov = vcov(model, cluster=~user)

se_home = c()
for (i in 1:22) {
    a <- rep(0, 44)
    a[i] <- 1
    a[i+22] <- 1
    se = c(sqrt(t(a) %*% vcov %*% a))
    se_home = append(se_home, se)
    print(se)
}


coef_home = c()
for (i in 1:22) {
    coef_home = append(coef_home, coefficients(model)[i] + coefficients(model)[i+22])
}

conf_int_home_left = coef_home - 1.96 * se_home
conf_int_home_right = coef_home + 1.96 * se_home

conf_int_dest_left = coefficients(model)[1:22] - 1.96 * summary(model, cluster=~user)$se[1:22]
conf_int_dest_right = coefficients(model)[1:22] + 1.96 * summary(model, cluster=~user)$se[1:22]

write.csv(coef_home, 'data/inset_information_coef_home.csv')
write.csv(coefficients(model)[1:22], 'data/inset_information_coef_dest.csv')

write.csv(conf_int_home_left, 'data/inset_information_se_home_left.csv')
write.csv(conf_int_home_right, 'data/inset_information_se_home_right.csv')

write.csv(conf_int_dest_left, 'data/inset_information_se_dest_left.csv')
write.csv(conf_int_dest_right, 'data/inset_information_se_dest_right.csv')


################## cluster #################

dta_cluster_dest_nonorm = read.csv(paste('data/cluster_dest_for_regression_22degree_sampled_10pct.csv', sep=""))
dta_cluster_dest_nonorm = dta_cluster_dest_nonorm[dta_cluster_dest_nonorm$d < 23,]
dta_cluster_dest_nonorm$home_dest_date <- paste(dta_cluster_dest_nonorm$home, dta_cluster_dest_nonorm$dest, dta_cluster_dest_nonorm$date, sep="_")
da = dta_cluster_dest_nonorm

da$dest_is_home = 1
da$dest_is_home[da$home != da$dest] = 0
da$cluster.2 = da$cluster.2 / 1000
da$cluster.3 = da$cluster.3 / 1000
da$cluster.4 = da$cluster.4 / 1000
da$cluster.5 = da$cluster.5 / 1000
da$cluster.6 = da$cluster.6 / 1000
da$cluster.7 = da$cluster.7 / 1000
da$cluster.8 = da$cluster.8 / 1000
da$cluster.9 = da$cluster.9 / 1000
da$cluster.10 = da$cluster.10 / 1000
da$cluster.11 = da$cluster.11 / 1000
da$cluster.12 = da$cluster.12 / 1000
da$cluster.13 = da$cluster.13 / 1000
da$cluster.14 = da$cluster.14 / 1000
da$cluster.15 = da$cluster.15 / 1000
da$cluster.16 = da$cluster.16 / 1000
da$cluster.17 = da$cluster.17 / 1000
da$cluster.18 = da$cluster.18 / 1000
da$cluster.19 = da$cluster.19 / 1000
da$cluster.20 = da$cluster.20 / 1000
da$cluster.21 = da$cluster.21 / 1000
da$cluster.22 = da$cluster.22 / 1000
da$date_user <- paste(da$date, da$user, sep="_")
da$date_dest_dest_is_home <- paste(da$date, da$dest, da$dest_is_home, sep="_")
da$degree_dest_is_home <- paste(da$d, da$dest_is_home, sep="_")
model <- feglm(if_move ~ cluster.2+cluster.2:dest_is_home+cluster.3+cluster.3:dest_is_home+cluster.4+cluster.4:dest_is_home+cluster.5+cluster.5:dest_is_home+cluster.6+cluster.6:dest_is_home+cluster.7+cluster.7:dest_is_home+cluster.8+cluster.8:dest_is_home+cluster.9+cluster.9:dest_is_home+cluster.10+cluster.10:dest_is_home+cluster.11+cluster.11:dest_is_home+cluster.12+cluster.12:dest_is_home+cluster.13+cluster.13:dest_is_home+cluster.14+cluster.14:dest_is_home+cluster.15+cluster.15:dest_is_home+cluster.16+cluster.16:dest_is_home+cluster.17+cluster.17:dest_is_home+cluster.18+cluster.18:dest_is_home+cluster.19+cluster.19:dest_is_home+cluster.20+cluster.20:dest_is_home+cluster.21+cluster.21:dest_is_home+cluster.22+cluster.22:dest_is_home| date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model, cluster=~user)

vcov = vcov(model, cluster=~user)

se_home = c()
for (i in 1:21) {
    a <- rep(0, 42)
    a[i] <- 1
    a[i+21] <- 1
    se = c(sqrt(t(a) %*% vcov %*% a))
    se_home = append(se_home, se)
    print(se)
}

coef_home = c()
for (i in 1:21) {
    coef_home = append(coef_home, coefficients(model)[i] + coefficients(model)[i+21])
}

conf_int_home_left = coef_home - 1.96 * se_home
conf_int_home_right = coef_home + 1.96 * se_home

conf_int_dest_left = coefficients(model)[1:21] - 1.96 * summary(model, cluster=~user)$se[1:21]
conf_int_dest_right = coefficients(model)[1:21] + 1.96 * summary(model, cluster=~user)$se[1:21]

write.csv(coef_home, 'data/inset_cluster_coef_home.csv')
write.csv(coefficients(model)[1:21], 'data/inset_cluster_coef_dest.csv')

write.csv(conf_int_home_left, 'data/inset_cluster_se_home_left.csv')
write.csv(conf_int_home_right, 'data/inset_cluster_se_home_right.csv')

write.csv(conf_int_dest_left, 'data/inset_cluster_se_dest_left.csv')
write.csv(conf_int_dest_right, 'data/inset_cluster_se_dest_right.csv')
