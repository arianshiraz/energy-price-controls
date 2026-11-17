# Figures for tests 1 and 2 (ggdist for uncertainty; Okabe-Ito colours).
# Reads the chart tables written from output/tables/ and saves PDF (paper) and PNG (README) to output/figures/.
# Run: Rscript code/13_figures.R

suppressPackageStartupMessages({
  library(readr); library(dplyr); library(ggplot2); library(ggdist); library(distributional); library(tidyplots)
})

root <- normalizePath(file.path(dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE))), ".."))
tab <- file.path(root, "output", "tables")
fig <- file.path(root, "output", "figures")
dir.create(fig, showWarnings = FALSE)
okabe <- as.vector(unclass(colors_discrete_okabeito))  # convert before mixing with hex strings
cols <- c(electricity = okabe[1], gas = okabe[2])

save_both <- function(p, name, w, h) {
  ggsave(file.path(fig, paste0(name, ".pdf")), p, width = w, height = h, device = cairo_pdf)
  ggsave(file.path(fig, paste0(name, ".png")), p, width = w, height = h, dpi = 300)
}

# Figure 1: test 2 event study -------------------------------------------------
es <- read_csv(file.path(tab, "fig_test2_eventstudy.csv"), show_col_types = FALSE) |>
  mutate(product = factor(product, levels = c("electricity", "gas"),
                          labels = c("Electricity (21 events, 16 countries)", "Gas (20 events, 16 countries)")),
         se = ifelse(is.na(se), 0, se))
p1 <- ggplot(es, aes(x = tau, colour = product)) +
  geom_hline(yintercept = 0, colour = "grey60", linewidth = 0.3) +
  geom_vline(xintercept = -0.5, linetype = 2, colour = "grey60", linewidth = 0.3) +
  stat_pointinterval(aes(xdist = NULL, ydist = dist_normal(coef, se)), .width = c(0.5, 0.95),
                     point_size = 1.8, interval_size_range = c(0.5, 1.4)) +
  facet_wrap(~product) +
  scale_colour_manual(values = unname(cols), guide = "none") +
  scale_x_continuous(breaks = -3:6) +
  labs(x = "Months from the end of the control or the scheduled step-up",
       y = "Excess change in the price index\n(100 log points, relative to month -1)",
       caption = "Point estimates with 50% and 95% intervals; event fixed effects; standard errors clustered by country.") +
  theme_classic(base_size = 9) +
  theme(strip.background = element_blank(), strip.text = element_text(face = "bold", hjust = 0),
        plot.caption = element_text(hjust = 0, colour = "grey30"))
save_both(p1, "fig1_test2_eventstudy", 6.5, 3.2)

# Figure 2: test 1 freeze coefficient across horizons ----------------------------
b <- read_csv(file.path(tab, "fig_test1_freeze.csv"), show_col_types = FALSE)
loo <- read_csv(file.path(tab, "fig_test1_leave_one_out.csv"), show_col_types = FALSE)
p2 <- ggplot(b, aes(x = factor(h))) +
  geom_hline(yintercept = 0, colour = "grey60", linewidth = 0.3) +
  geom_point(data = loo, aes(y = b1), colour = "grey70", size = 0.9,
             position = position_nudge(x = -0.18)) +
  stat_pointinterval(aes(ydist = dist_normal(coef, se_hc3)), .width = c(0.5, 0.95), colour = okabe[5],
                     point_size = 2, interval_size_range = c(0.5, 1.4)) +
  labs(x = "Months after July 2021", y = "Freeze coefficient b1\n(100 log points)",
       caption = paste0("Coloured: estimate with 50% and 95% intervals (HC3), 27 countries.\n",
                        "Grey: estimates leaving out one country at a time.")) +
  theme_classic(base_size = 9) +
  theme(plot.caption = element_text(hjust = 0, colour = "grey30"))
save_both(p2, "fig2_test1_freeze_by_horizon", 5.2, 3.2)
cat("saved figures to", fig, "\n")
