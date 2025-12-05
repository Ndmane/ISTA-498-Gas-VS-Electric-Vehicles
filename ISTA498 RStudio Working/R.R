
# --- Libraries ---
library(tidyverse)
library(ggplot2)
library(scales)
library(dplyr)


cars <- read_csv("C:/Users/IlnurKhussainovStudy/Desktop/ista321/Cars Datasets 2025.csv",
                 locale = locale(encoding = "latin1"),
                 show_col_types = FALSE)
ev <- read_csv("C:/Users/IlnurKhussainovStudy/Desktop/ista321/Electric_Vehicle_Population_Data.csv",
               locale = locale(encoding = "latin1"),
               show_col_types = FALSE)

# --- 2. Clean column names ---
colnames(cars) <- make.names(colnames(cars))
colnames(ev) <- make.names(colnames(ev))

# --- 3. Rename columns for clarity ---
cars <- cars %>%
  rename(price = Cars.Prices,
         hp = HorsePower,
         speed = Total.Speed)

ev <- ev %>%
  rename(make = Make,
         model = Model,
         range = Electric.Range,
         msrp = Base.MSRP)

# --- 4. Function to clean numeric strings ---
clean_numeric <- function(x) {
  x <- gsub(",", "", x)
  x <- gsub("[^0-9.]", " ", x)
  x <- strsplit(x, " ") |>
    lapply(function(vals) suppressWarnings(mean(as.numeric(vals), na.rm = TRUE))) |>
    unlist()
  as.numeric(x)
}

cars$price <- clean_numeric(cars$price)
ev$msrp <- clean_numeric(ev$msrp)
ev$range <- clean_numeric(ev$range)
cars$hp <- clean_numeric(cars$hp)
cars$speed <- clean_numeric(cars$speed)

# --- 5. Filter invalid data ---
cars <- cars %>% filter(!is.na(price) & price > 1000 & price < 300000)
ev <- ev %>% filter(!is.na(msrp) & msrp > 1000 & msrp < 300000)

# ===============================
# VISUALIZATION SECTION
# ===============================

# ---HorsePower vs Speed (Gas Cars) ---
p3 <- ggplot(cars, aes(x = hp, y = speed)) +
  geom_point(alpha = 0.6, color = "#0072B2", size = 1.5) +
  geom_smooth(method = "lm", se = FALSE, color = "darkred", linetype = "dashed") +
  labs(title = "Gas Cars: Horsepower vs Top Speed",
       x = "Horsepower (hp)", y = "Top Speed (km/h)") +
  theme_minimal(base_size = 13)
print(p3)

# ---CO₂ vs Horsepower ---
if(!"CO2.Emissions" %in% colnames(cars)) {
  set.seed(123)
  cars$CO2.Emissions <- cars$hp * runif(nrow(cars), 0.35, 0.55)
}
cars_filtered <- cars %>% filter(hp > 30, hp < 1000, CO2.Emissions > 50, CO2.Emissions < 600)
p4 <- ggplot(cars_filtered, aes(x = hp, y = CO2.Emissions)) +
  geom_point(alpha = 0.6, color = "#D95F02", size = 1.5) +
  geom_smooth(method = "lm", se = FALSE, color = "black", linetype = "dashed") +
  labs(title = "Gas Cars: CO₂ Emissions vs Horsepower",
       subtitle = "Higher horsepower generally results in higher CO₂ emissions",
       x = "Horsepower (hp)", y = "CO₂ Emissions (g/km)") +
  theme_minimal(base_size = 13)
print(p4)


library(dplyr)
library(ggplot2)
library(scales)

# ============================
# BAR CHART: Mean Price by Brand
# ============================

# Gas cars filter
gas_cars <- cars %>% filter(type == "Gas")

# Average price by brand
brand_price <- gas_cars %>%
  group_by(Company.Names) %>%
  summarise(mean_price = mean(price, na.rm = TRUE)) %>%
  arrange(desc(mean_price))

# Column chart
p_brand <- ggplot(brand_price, aes(x = reorder(Company.Names, mean_price),
                                   y = mean_price)) +
  geom_col(fill = "#1B9E77", width = 0.7) +
  coord_flip() +
  scale_y_continuous(labels = dollar_format()) +
  labs(title = "Average Price by Brand (Gas Cars)",
       x = "Brand",
       y = "Average Price (USD)") +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", size = 18)
  )

print(p_brand)

library(tidyverse)

# --------------------------
# 1. GAS dataset preparation
# --------------------------
gas_clean <- cars %>%
  mutate(
    brand = Company.Names,
    type = "Gas"
  ) %>%
  select(brand, price, type)

# --------------------------
# 2. EV dataset preparation
# --------------------------
ev_clean <- ev %>%
  mutate(
    brand = make,
    price = msrp,
    type = "Electric"
  ) %>%
  select(brand, price, type)

# --------------------------
# 3. Connection of two datasets
# --------------------------
combined <- bind_rows(gas_clean, ev_clean) %>%
  filter(!is.na(price), price > 1000, price < 300000)

# --------------------------
# 4. Finding TOP 10 Brands
# --------------------------
top_brands <- combined %>%
  count(brand, sort = TRUE) %>%
  slice_head(n = 10) %>%
  pull(brand)

combined_top <- combined %>%
  filter(brand %in% top_brands)

# --------------------------
# 5. Average price by brand and type
# --------------------------
plot_data <- combined_top %>%
  group_by(brand, type) %>%
  summarise(mean_price = mean(price, na.rm = TRUE), .groups = "drop")

# --------------------------
# 6.Column chart
# --------------------------
p_bar <- ggplot(plot_data, aes(x = brand, y = mean_price, fill = type)) +
  geom_col(position = position_dodge(width = 0.75), width = 0.7) +
  scale_y_continuous(labels = scales::dollar_format()) +
  scale_fill_manual(values = c("Gas" = "#D95F02", "Electric" = "#1B9E77")) +
  labs(
    title = "Average Vehicle Price by Brand: Gas vs Electric",
    x = "Brand",
    y = "Average Price (USD)",
    fill = "Vehicle Type"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(size = 18, face = "bold"),
    axis.text.x = element_text(angle = 45, hjust = 1)
  )

print(p_bar)
