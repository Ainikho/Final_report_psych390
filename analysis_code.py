import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
import rpy2.robjects.lib.ggplot2 as ggplot2

pandas2ri.activate()

# Load data
df = pd.read_csv("stroop_combined.csv")

# Convert categorical variables
df["participant"] = df["participant"].astype(str)
df["congruent"] = df["congruent"].astype(int)
df["correct"] = df["correct"].astype(int)

# Convert to R dataframe
r_df = pandas2ri.py2rpy(df)

r_script = """
library(lme4)
library(lmerTest)
library(ggplot2)

# Load data from Python
df <- data

# Check if data is loaded properly
message("Data preview: ", head(df))

# Try fitting models and capturing any errors
tryCatch({
  # Linear Mixed Model for Reaction Time
  model_rt <- lmer(reaction_time_ms ~ congruent * Trial + (1 + Trial | participant), data=df)
  
  # Generalized Linear Mixed Model for Accuracy (Logistic Regression)
  model_acc <- glmer(correct ~ congruent * Trial + (1 + Trial | participant), 
                     data=df, 
                     family=binomial)
  
  # Capture summaries as text
  rt_summary_text <- capture.output(summary(model_rt))
  acc_summary_text <- capture.output(summary(model_acc))

  # Return summaries to Python
  message("Reaction Time Model Summary:\n", paste(rt_summary_text, collapse="\n"))
  message("Accuracy Model Summary:\n", paste(acc_summary_text, collapse="\n"))
  
  list(rt_summary_text, acc_summary_text)
  
}, error = function(e) {
  # Capture any errors
  message("Error in model fitting: ", e$message)
  return(list("Error in model fitting"))
})

# plot for RXN time
rt_plot <- ggplot(df, aes(x=Trial, y=reaction_time_ms, color=factor(congruent))) + 
           geom_line() +
           labs(title="Reaction Time Across Trials by Congruency",
                x="Trial Number", 
                y="Reaction Time (ms)") +
           theme_minimal()

# Save reaction time plot
ggsave("reaction_time_plot.png", plot=rt_plot)

# plot for Accuracy 
acc_plot <- ggplot(df, aes(x=Trial, y=correct, color=factor(congruent))) + 
            geom_line() +
            labs(title="Accuracy Across Trials by Congruency",
                 x="Trial Number", 
                 y="Accuracy (Proportion Correct)") +
            theme_minimal()

# Save accuracy plot
ggsave("accuracy_plot.png", plot=acc_plot)

"""

# Pass data from Python to R
ro.globalenv["data"] = r_df

# Run the R script
results = ro.r(r_script)

# Unwrap and print each model summary
rt_summary = results[0]
acc_summary = results[1]

print("Reaction Time Model Summary:")
print(rt_summary)

print("\nAccuracy Model Summary:")
print(acc_summary)