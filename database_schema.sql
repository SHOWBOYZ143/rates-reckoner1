-- Create the gazetted_rates table
CREATE TABLE gazetted_rates (
  id BIGSERIAL PRIMARY KEY,
  year INT NOT NULL,
  rate_type VARCHAR(255) NOT NULL,
  service_category VARCHAR(255) NOT NULL,
  service_name VARCHAR(255) NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  unit VARCHAR(100),
  remarks TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(255),
  UNIQUE(year, rate_type, service_category, service_name)
);

-- Create an index for faster queries
CREATE INDEX idx_gazetted_rates_year ON gazetted_rates(year);
CREATE INDEX idx_gazetted_rates_service ON gazetted_rates(service_category, service_name);
CREATE INDEX idx_gazetted_rates_type ON gazetted_rates(rate_type);

-- Create audit log table to track updates
CREATE TABLE rates_audit_log (
  id BIGSERIAL PRIMARY KEY,
  rate_id BIGINT REFERENCES gazetted_rates(id),
  old_amount DECIMAL(12, 2),
  new_amount DECIMAL(12, 2),
  modified_by VARCHAR(255),
  modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  notes TEXT
);

-- Create a view for the latest rates
CREATE VIEW latest_rates AS
SELECT * FROM gazetted_rates
WHERE year = (SELECT MAX(year) FROM gazetted_rates);
