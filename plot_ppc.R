library(tidyverse)

args = commandArgs(trailingOnly = T)
print(args)

topic.perword.data <- read_tsv(args[1], col_names = c("Word", "Replicated", "Discrepancy", "Rank", "Probability"))

topic.perword.data$Alpha <- ifelse(topic.perword.data$Replicated == "Replicated", 0.8, 1.0)
topic.perword.data$Colour <- ifelse(topic.perword.data$Replicated == "Replicated", 0, 1)

max.discrepancy = max(topic.perword.data$Discrepancy)

p <- ggplot(topic.perword.data, aes(x=Discrepancy, y=Rank, alpha=Alpha))
p + geom_point(aes(size=log(Probability), shape=Replicated)) +
  geom_text(data=subset(topic.perword.data, Replicated %in% c("Real")), aes(x=Discrepancy, y=Rank, label=Word), hjust=-0.5) +
  scale_y_reverse() + scale_colour_grey() + theme_bw() + theme(legend.position = "none") + xlim(0, 1.1 * max.discrepancy)

ggsave(args[2], width=5, height=5)
