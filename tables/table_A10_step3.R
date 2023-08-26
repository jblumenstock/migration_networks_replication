library(fixest)


# ################### Disaggregating the network support effect by the strength of supported ties ########################

da = read.csv("data/dest_home_d_s_l_support_strong.csv")

da$dest_is_home = 1
da$dest_is_home[da$home != da$dest] = 0
da$user_dest <- paste(da$user, da$dest, sep="_")
da$user_degree_dest <- paste(da$user, da$d, sep="_")
da$home_dest_user <- paste(da$home, da$dest, da$user, sep="_")
da$home_dest_date <- paste(da$home, da$dest, da$date, sep="_")
da$date_user <- paste(da$date, da$user, sep="_")
da$date_dest_dest_is_home <- paste(da$date, da$dest, da$dest_is_home, sep="_")
da$degree_dest_is_home <- paste(da$d, da$dest_is_home, sep="_")

da$strong_tie = da$strong_tie / 1000
da$support_sss = da$support_sss / 1000
da$support_sws = da$support_sws / 1000
da$support_ssw = da$support_ssw / 1000
da$support_sww = da$support_sww / 1000
da$support_wss = da$support_wss / 1000
da$support_wws = da$support_wws / 1000
da$support_wsw = da$support_wsw / 1000
da$support_www = da$support_www / 1000

df = read.csv("data/dest_home_d_s_l.csv")
df$s_dest = df$s_dest/1000
df$dest = df$dest_dest
a = df[,c('user', 'date', 's_dest', 'dest')]
df2 = merge(da[,c('user','date', 'home', 'dest','strong_tie', 'd', 'if_move')], a, by=c('user', 'date', 'dest'))
df2$dest_is_home = 1
df2$dest_is_home[df2$home != df2$dest] = 0
df2$user_dest <- paste(df2$user, df2$dest, sep="_")
df2$user_degree_dest <- paste(df2$user, df2$d, sep="_")
df2$home_dest_user <- paste(df2$home, df2$dest, df2$user, sep="_")
df2$home_dest_date <- paste(df2$home, df2$dest, df2$date, sep="_")
df2$date_user <- paste(df2$date, df2$user, sep="_")
df2$date_dest_dest_is_home <- paste(df2$date, df2$dest, df2$dest_is_home, sep="_")
df2$degree_dest_is_home <- paste(df2$d, df2$dest_is_home, sep="_")

model_0 <- feglm(if_move ~ s_dest + s_dest:dest_is_home + strong_tie + strong_tie:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, df2, vcov = ~user, family = binomial("logit"))
summary(model_0, cluster=~user)

mod0_vcov = vcov(model_0, cluster=~user)
mod0_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% mod0_vcov %*% a))
mod0_se_home = append(mod0_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% mod0_vcov %*% a))
mod0_se_home = append(mod0_se_home, se)

mod0_coef_home = c(
    coefficients(model_0)[1] + coefficients(model_0)[3], 
    coefficients(model_0)[2] + coefficients(model_0)[4]
)

summary(model_0, cluster=~user)
mod0_coef_home
mod0_se_home
pnorm(-abs(mod0_coef_home) / mod0_se_home)



model_1 <- feglm(if_move ~ support_sss + support_sss:dest_is_home + strong_tie + strong_tie:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
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



model_2 <- feglm(if_move ~  support_sws + support_sws:dest_is_home + strong_tie + strong_tie:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
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


model_3 <- feglm(if_move ~  support_ssw + support_ssw:dest_is_home + strong_tie + strong_tie:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_3, cluster=~user)

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


model_4 <- feglm(if_move ~  support_sww + support_sww:dest_is_home + strong_tie + strong_tie:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_4, cluster=~user)

model_4_vcov = vcov(model_4, cluster=~user)
model_4_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% model_4_vcov %*% a))
model_4_se_home = append(model_4_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% model_4_vcov %*% a))
model_4_se_home = append(model_4_se_home, se)

model_4_coef_home = c(
    coefficients(model_4)[1] + coefficients(model_4)[3], 
    coefficients(model_4)[2] + coefficients(model_4)[4]
)

summary(model_4, cluster=~user)
model_4_coef_home
model_4_se_home
pnorm(-abs(model_4_coef_home) / model_4_se_home)


model_5 <- feglm(if_move ~  support_wss + support_wss:dest_is_home + strong_tie + strong_tie:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_5, cluster=~user)

model_5_vcov = vcov(model_5, cluster=~user)
model_5_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% model_5_vcov %*% a))
model_5_se_home = append(model_5_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% model_5_vcov %*% a))
model_5_se_home = append(model_5_se_home, se)

model_5_coef_home = c(
    coefficients(model_5)[1] + coefficients(model_5)[3], 
    coefficients(model_5)[2] + coefficients(model_5)[4]
)

summary(model_5, cluster=~user)
model_5_coef_home
model_5_se_home
pnorm(-abs(model_5_coef_home) / model_5_se_home)


model_6 <- feglm(if_move ~  support_wws + support_wws:dest_is_home + strong_tie + strong_tie:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_6, cluster=~user)

model_6_vcov = vcov(model_6, cluster=~user)
model_6_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% model_6_vcov %*% a))
model_6_se_home = append(model_6_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% model_6_vcov %*% a))
model_6_se_home = append(model_6_se_home, se)

model_6_coef_home = c(
    coefficients(model_6)[1] + coefficients(model_6)[3], 
    coefficients(model_6)[2] + coefficients(model_6)[4]
)

summary(model_6, cluster=~user)
model_6_coef_home
model_6_se_home
pnorm(-abs(model_6_coef_home) / model_6_se_home)


model_7 <- feglm(if_move ~  support_wsw + support_wsw:dest_is_home + strong_tie + strong_tie:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_7, cluster=~user)

model_7_vcov = vcov(model_7, cluster=~user)
model_7_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% model_7_vcov %*% a))
model_7_se_home = append(model_7_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% model_7_vcov %*% a))
model_7_se_home = append(model_7_se_home, se)

model_7_coef_home = c(
    coefficients(model_7)[1] + coefficients(model_7)[3], 
    coefficients(model_7)[2] + coefficients(model_7)[4]
)

summary(model_7, cluster=~user)
model_7_coef_home
model_7_se_home
pnorm(-abs(model_7_coef_home) / model_7_se_home)


model_8 <- feglm(if_move ~  support_www + support_www:dest_is_home + strong_tie + strong_tie:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_8, cluster=~user)

model_8_vcov = vcov(model_8, cluster=~user)
model_8_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% model_8_vcov %*% a))
model_8_se_home = append(model_8_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% model_8_vcov %*% a))
model_8_se_home = append(model_8_se_home, se)

model_8_coef_home = c(
    coefficients(model_8)[1] + coefficients(model_8)[3], 
    coefficients(model_8)[2] + coefficients(model_8)[4]
)

summary(model_8, cluster=~user)
model_8_coef_home
model_8_se_home
pnorm(-abs(model_8_coef_home) / model_8_se_home)


model_9 <- feglm(if_move ~  support_sss + support_sss:dest_is_home + support_sws + support_sws:dest_is_home + support_ssw + support_ssw:dest_is_home + support_sww + support_sww:dest_is_home + support_wss + support_wss:dest_is_home + support_wws + support_wws:dest_is_home + support_wsw + support_wsw:dest_is_home + support_www + support_www:dest_is_home + strong_tie + strong_tie:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da, vcov = ~user, family = binomial("logit"))
summary(model_9, cluster=~user)

model_9_vcov = vcov(model_9, cluster=~user)
model_9_se_home = c()
a <- rep(0,18)
a[1] <- 1
a[10] <- 1
se = c(sqrt(t(a) %*% model_9_vcov %*% a))
model_9_se_home = append(model_9_se_home, se)

a <- rep(0,18)
a[2] <- 1
a[11] <- 1
se = c(sqrt(t(a) %*% model_9_vcov %*% a))
model_9_se_home = append(model_9_se_home, se)

a <- rep(0,18)
a[3] <- 1
a[12] <- 1
se = c(sqrt(t(a) %*% model_9_vcov %*% a))
model_9_se_home = append(model_9_se_home, se)

a <- rep(0,18)
a[4] <- 1
a[13] <- 1
se = c(sqrt(t(a) %*% model_9_vcov %*% a))
model_9_se_home = append(model_9_se_home, se)

a <- rep(0,18)
a[5] <- 1
a[14] <- 1
se = c(sqrt(t(a) %*% model_9_vcov %*% a))
model_9_se_home = append(model_9_se_home, se)

a <- rep(0,18)
a[6] <- 1
a[15] <- 1
se = c(sqrt(t(a) %*% model_9_vcov %*% a))
model_9_se_home = append(model_9_se_home, se)

a <- rep(0,18)
a[7] <- 1
a[16] <- 1
se = c(sqrt(t(a) %*% model_9_vcov %*% a))
model_9_se_home = append(model_9_se_home, se)

a <- rep(0,18)
a[8] <- 1
a[17] <- 1
se = c(sqrt(t(a) %*% model_9_vcov %*% a))
model_9_se_home = append(model_9_se_home, se)

a <- rep(0,18)
a[9] <- 1
a[18] <- 1
se = c(sqrt(t(a) %*% model_9_vcov %*% a))
model_9_se_home = append(model_9_se_home, se)


model_9_coef_home = c(
    coefficients(model_9)[1] + coefficients(model_9)[10], 
    coefficients(model_9)[2] + coefficients(model_9)[11], 
    coefficients(model_9)[3] + coefficients(model_9)[12], 
    coefficients(model_9)[4] + coefficients(model_9)[13], 
    coefficients(model_9)[5] + coefficients(model_9)[14], 
    coefficients(model_9)[6] + coefficients(model_9)[15], 
    coefficients(model_9)[7] + coefficients(model_9)[16], 
    coefficients(model_9)[8] + coefficients(model_9)[17], 
    coefficients(model_9)[9] + coefficients(model_9)[18]
)

summary(model_9, cluster=~user)
model_9_coef_home
model_9_se_home
pnorm(-abs(model_9_coef_home) / model_9_se_home)
