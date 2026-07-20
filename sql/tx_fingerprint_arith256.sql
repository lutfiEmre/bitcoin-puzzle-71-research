-- Arithmetic series: exactly 256 outputs stepping by 100000 sats each

WITH outputs AS (
  SELECT
    transaction_hash,
    block_number,
    block_timestamp,
    `index` AS output_index,
    CAST(value AS BIGNUMERIC) AS value_sats
  FROM `bigquery-public-data.crypto_bitcoin.outputs`
  WHERE block_timestamp >= TIMESTAMP('2013-01-01')
    AND block_timestamp < TIMESTAMP('2017-01-01')
),

candidate_txs AS (
  SELECT transaction_hash
  FROM outputs
  GROUP BY transaction_hash
  HAVING COUNT(*) = 256
),

ordered AS (
  SELECT
    o.*,
    value_sats
      - LAG(value_sats) OVER (
          PARTITION BY transaction_hash
          ORDER BY output_index
        ) AS value_delta
  FROM outputs o
  JOIN candidate_txs USING (transaction_hash)
),

summary AS (
  SELECT
    transaction_hash,
    ANY_VALUE(block_number) AS block_number,
    ANY_VALUE(block_timestamp) AS block_timestamp,
    COUNT(*) AS output_count,
    COUNTIF(output_index = 0 OR value_delta = 100000) AS matching_steps,
    MIN(value_sats) AS min_value,
    MAX(value_sats) AS max_value,
    SUM(value_sats) AS total_value
  FROM ordered
  GROUP BY transaction_hash
)

SELECT *
FROM summary
WHERE output_count = 256
  AND matching_steps = 256
ORDER BY block_timestamp;
