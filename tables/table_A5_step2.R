library(fixest)


######################### adjacent vs non-adjacent ###################
da = read.csv("data/dest_home_d_s_l_adjacent.csv")

da$dest_is_home = 1
da$dest_is_home[da$home_dest != da$dest_dest] = 0
da$d_dest = da$d_dest/1000
da$l_dest = da$l_dest/1000
da$s_dest = da$s_dest/1000
da$date_user <- paste(da$date, da$user, sep="_")
da$date_dest_dest_is_home <- paste(da$date, da$dest_dest, da$dest_is_home, sep="_")
da$degree_dest_is_home <- paste(da$d_dest, da$dest_is_home, sep="_")

da_adjacent = da[(da$if_neighbor==1) | (da$home_dest==da$dest_dest),]
da_nonadjacent = da[(da$if_neighbor==0) | (da$home_dest==da$dest_dest),]

# adjacent
model_adjacent <- feglm(if_move ~ s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da_adjacent, vcov = ~user, family = binomial("logit"))
summary(model_adjacent, cluster=~user)

model_adjacent_vcov = vcov(model_adjacent, cluster=~user)
model_adjacent_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% model_adjacent_vcov %*% a))
model_adjacent_se_home = append(model_adjacent_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% model_adjacent_vcov %*% a))
model_adjacent_se_home = append(model_adjacent_se_home, se)

model_adjacent_coef_home = c(
    coefficients(model_adjacent)[1] + coefficients(model_adjacent)[3], 
    coefficients(model_adjacent)[2] + coefficients(model_adjacent)[4]
)

summary(model_adjacent, cluster=~user)
model_adjacent_coef_home
model_adjacent_se_home
pnorm(-abs(model_adjacent_coef_home) / model_adjacent_se_home)


# nonadjacent
model_nonadjacent <- feglm(if_move ~ s_dest+s_dest:dest_is_home+l_dest+l_dest:dest_is_home | date_user + date_dest_dest_is_home + degree_dest_is_home, da_nonadjacent, vcov = ~user, family = binomial("logit"))
summary(model_nonadjacent, cluster=~user)

model_nonadjacent_vcov = vcov(model_nonadjacent, cluster=~user)
model_nonadjacent_se_home = c()
a <- rep(0, 4)
a[1] <- 1
a[3] <- 1
se = c(sqrt(t(a) %*% model_nonadjacent_vcov %*% a))
model_nonadjacent_se_home = append(model_nonadjacent_se_home, se)

a <- rep(0, 4)
a[2] <- 1
a[4] <- 1
se = c(sqrt(t(a) %*% model_nonadjacent_vcov %*% a))
model_nonadjacent_se_home = append(model_nonadjacent_se_home, se)

model_nonadjacent_coef_home = c(
    coefficients(model_nonadjacent)[1] + coefficients(model_nonadjacent)[3], 
    coefficients(model_nonadjacent)[2] + coefficients(model_nonadjacent)[4]
)

summary(model_nonadjacent, cluster=~user)
model_nonadjacent_coef_home
model_nonadjacent_se_home
pnorm(-abs(model_nonadjacent_coef_home) / model_nonadjacent_se_home)

