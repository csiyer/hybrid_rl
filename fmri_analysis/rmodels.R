library(lme4)
library(ggplot2)
library(interplot)
library(lmerTest)
library(showtext)
font_add("Palatino", "/System/Library/Fonts/Supplemental/Palatino.ttc") # macOS path
showtext_auto()  # Turn on showtext

data <- read.csv('/Users/chrisiyer/_Current/lab/code/hybrid_rl/fmri_analysis/data/hybrid_data.csv')

###################################### Incremental / Episodic
model_incep <- glmer(ChooseRed ~ OldValRed + Q_red + (1 + OldValRed + Q_red | Sub),
                     data=data, family=binomial)
summary(model_incep)

library(rstan)
library(loo)
fit<-load('/Users/chrisiyer/_Current/lab/code/hybrid_rl/fmri_analysis/data/stanfit_rl')
log_lik_standard<-extract_log_lik(standard_fit)
looc_standard<-loo(log_lik_standard,cores=4)
# waic_standard<-waic(log_lik_standard)

fit2<-load('/Users/chrisiyer/_Current/lab/code/hybrid_rl/fmri_analysis/data/stanfit_hybridrl')
log_lik_hybrid<-extract_log_lik(hybrid1_fit)
looc_hybrid<-loo(log_lik_hybrid,cores=4)
# waic_hybrid<-waic(log_lik_hybrid)


###################################### RT
model_rt <- lmer(RT ~ ObjPP + Q_diff + (1+ ObjPP + Q_diff | Sub), data=data)
summary(model_rt)


###################################### Reversal interactions
data$RevT_c <- data$RevT - 12
data$EncRevT_c <- data$EncRevT - 12
data$ObjPP_c <- data$ObjPP-0.5
data$PP_c <- data$PP - 0.5
data$oneback_choosered_contrast <- ifelse(dplyr::lag(data$ChooseRed) == 1, 1, -1)
data$oneback_outcome_red <- data$oneback_choosered_contrast*data$PP_c

model_feedback <- glmer(ChooseRed ~ oneback_outcome_red*RevT_c+(oneback_outcome_red*RevT_c|Sub),
                        data=data, family=binomial)
summary(model_feedback)

p <- interplot(model_feedback, 'oneback_outcome_red', 'RevT_c') +
  theme_classic(base_family = "Palatino") + ggtitle('     Deck Feedback')+
  theme(text = element_text(size = 24), legend.position = "none") +
  xlab('Trials Since Reversal') +
  ylab('Effect of Last Deck \nFeedback on Next Choice') +
  scale_x_continuous(labels = c(2, 7, 12, 17, 25, 30))
p$layers[[2]]$aes_params$fill <- "#1f77b4"
# redraw the line so it goes on top
p <- p + geom_line(data=p$data,aes(x = fake, y = coef1), color = "black", size = 3)
p



model_encoding <- glmer(OldObjC ~ ObjPP_c*EncRevT_c + (ObjPP_c*EncRevT_c|Sub),
                        data=data,family=binomial)
summary(model_encoding)


q<-interplot(model_encoding,'ObjPP_c','EncRevT_c')+
  theme_classic(base_family = "Palatino")+theme(text=element_text(size=24),legend.position="none")+
  ggtitle('     Object Value')+
  #scale_fill_brewer(palette = "Blues",direction=-1)+
  xlab('Trials Since Reversal\nat Encoding')+ylab('Effect of Object Value \non Retrieval Choice')+
  scale_x_continuous(labels=c(2,7,12,17,25,30))
q$layers[[2]]$aes_params$fill <- "#1f77b4"
# redraw the line so it goes on top
q <- q + geom_line(data=q$data,aes(x = fake, y = coef1), color = "black", size = 3)
q


###################################### Reversal learning
model_lucky <- glmer(LuckyDeckC ~ RevT_c + (1+ RevT_c | Sub), data=data, family=binomial)
summary(model_lucky)


###################################### Encoding effects
new_columns <- c(
  "Outcome_enc", "Q_chosen_enc", "PE_enc", "PE_enc_unsigned", "PE_enc_sign",
  "PE_prevtrial_enc", "PE_prevtrial_enc_unsigned", "PE_prevtrial_enc_sign",
  "RT_enc", "RevT_enc_centered"
)
data[new_columns] <- NA
for (i in which(data$OldT == 1)) {
  row <- data[i, ]
  enc_idx <- which(data$Trial == row$encTrialNum & data$Sub == row$Sub)
  if (length(enc_idx) == 0) {
    next
  }
  enc_idx <- enc_idx[1]
  data$Q_chosen_enc[i] <- data$Q_chosen[enc_idx]
  data$PE_enc[i] <- data$PE[enc_idx]
  if (enc_idx != 1) {
    data$PE_prevtrial_enc[i] <- data$PE[enc_idx - 1]
  }
}
data$PE_enc_unsigned <- abs(data$PE_enc)
data$PE_enc_sign <- sign(data$PE_enc)
data$PE_prevtrial_enc_unsigned <- abs(data$PE_prevtrial_enc)
data$PE_prevtrial_enc_sign <- sign(data$PE_prevtrial_enc)


model_submem <- glmer(OptObj ~ ObjPP + Q_chosen_enc + PE_enc + PE_prevtrial_enc + 
                        EncRevT_c + Q_chosen + (1|Sub),data=data, family=binomial)
summary(model_submem)

