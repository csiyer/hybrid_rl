library(lme4)
library(ggplot2)
library(interplot)

data <- read.csv('/Users/chrisiyer/_Current/lab/code/hybrid_rl/fmri_analysis/data/hybrid_data.csv')

data$RevT_c <- data$RevT - 12
data$EncRevT_c <- data$EncRevT - 12
data$ObjPP_c <- data$ObjPP-0.5
data$PP_c <- data$PP - 0.5
data$oneback_choosered_contrast <- ifelse(dplyr::lag(data$ChooseRed) == 1, 1, -1)
data$oneback_outcome_red <- data$oneback_choosered_contrast*data$PP_c

model_feedback <- glmer(ChooseRed ~ oneback_outcome_red*RevT_c+(oneback_outcome_red*RevT_c|Sub),
                        data=data, family=binomial)

p <- interplot(model_feedback, 'oneback_outcome_red', 'RevT_c') +
  theme_classic() +
  theme(text = element_text(size = 20), legend.position = "none") +
  xlab('Trials Since Reversal') +
  ylab('Effect of Deck Feedback \non Next Deck Choice') +
  scale_x_continuous(labels = c(2, 7, 12, 17, 25, 30))
p$layers[[2]]$aes_params$fill <- "#1f77b4"
# redraw the line so it goes on top
p <- p + geom_line(data=p$data,aes(x = fake, y = coef1), color = "black", size = 3)
p



model_encoding <- glmer(OldObjC ~ ObjPP_c*EncRevT_c + (ObjPP_c*EncRevT_c|Sub),
                        data=data,family=binomial)


q<-interplot(model_encoding,'ObjPP_c','EncRevT_c')+
  theme_classic()+theme(text=element_text(size=20),legend.position="none")+
  #scale_fill_brewer(palette = "Blues",direction=-1)+
  xlab('Trials Since Reversal\nat Encoding')+ylab('Effect of Object Feedback \non Retrieval Choice')+
  scale_x_continuous(labels=c(2,7,12,17,25,30))
q$layers[[2]]$aes_params$fill <- "#1f77b4"
# redraw the line so it goes on top
q <- q + geom_line(data=q$data,aes(x = fake, y = coef1), color = "black", size = 3)
q

