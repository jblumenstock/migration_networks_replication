library(lfe)
library(stargazer)

da = read.csv("data/dest_home_d_s_l.csv")
da$dest_is_home = 1
da$dest_is_home[da$home_dest != da$dest_dest] = 0
da = da[da$d_home>1 & da$d_dest>1,]
da$d_dest = da$d_dest/1000
da$l_dest = da$l_dest/1000
da$s_dest = da$s_dest/1000
da$date_user <- paste(da$date, da$user, sep="_")
da$user_dest <- paste(da$user, da$dest_dest, sep="_")
da$user_degree_dest <- paste(da$user, da$d_dest, sep="_")
da$user_month <- paste(da$user, da$date, sep="_")
da$home_dest_user <- paste(da$home_dest, da$dest_dest, da$user, sep="_")
da$home_dest_date <- paste(da$home_dest, da$dest_dest, da$date, sep="_")

model_1 <- felm(if_move ~ s_dest+l_dest|home_dest_date+d_dest+user|0|home_dest_date+user, data = da)
summary(model_1)
model_2 <- felm(if_move ~ s_dest+l_dest|home_dest_date+d_dest+user_month|0|home_dest_date+user, data = da)
summary(model_2)
model_3 <- felm(if_move ~ s_dest+l_dest|home_dest_date+d_dest+user_dest|0|home_dest_date+user, data = da)
summary(model_3)
model_4 <- felm(if_move ~ s_dest+l_dest|home_dest_date+d_dest+user_degree_dest|0|home_dest_date+user, data = da)
summary(model_4)
model_5 <- felm(if_move ~ s_dest+l_dest|home_dest_user+d_dest+date|0|home_dest_date+user, data = da)
summary(model_5)
stargazer(model_1, model_2, model_3, model_4, model_5,
         title="Regression results of pull and push",
         no.space=TRUE,
         dep.var.caption = "",
         dep.var.labels.include = FALSE,
         covariate.labels=c("destination support",
                            "destination information"),
         omit.stat = c("adj.rsq", "f", "ser"),
         table.layout ="-#-ts-n",
         digits=4,
         digits.extra=4)
