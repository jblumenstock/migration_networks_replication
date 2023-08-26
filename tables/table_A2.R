library(fixest)


######################### only migrants ###################
da = read.csv("data/dest_home_d_s_l_migrants_only.csv")

da$d_dest = da$d_dest/1000
da$l_dest = da$l_dest/1000
da$s_dest = da$s_dest/1000
da$date_user <- paste(da$date, da$user, sep="_")
da$date_dest <- paste(da$date, da$dest_dest, sep="_")
da$date_dest_dest_is_home <- paste(da$date, da$dest_dest, da$dest_is_home, sep="_")
da$degree_dest_is_home <- paste(da$d_dest, da$dest_is_home, sep="_")

mod1_migrant <- feglm(if_move ~ d_dest+s_dest+l_dest | date_user, da, vcov = ~user, 
             family = binomial("logit"))
summary(mod1_migrant, cluster=~user)

mod2_migrant <- feglm(if_move ~ d_dest+s_dest+l_dest | date_user + date_dest, da, vcov = ~user, 
             family = binomial("logit"), glm.iter=50)
summary(mod2_migrant, cluster=~user)

mod3_migrant <- feglm(if_move ~ s_dest+l_dest | date_user + date_dest + d_dest, da, vcov = ~user, 
             family = binomial("logit"))
summary(mod3_migrant, cluster=~user)
