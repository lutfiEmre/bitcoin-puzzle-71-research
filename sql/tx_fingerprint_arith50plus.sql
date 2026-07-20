-- Relaxed: 50+ outputs with constant +100000 sat steps

WITH ordered AS (
  SELECT
    transaction_hash,
    block_number,
    block_timestamp,
    `index` AS output_index,
    CAST(value AS BIGNUMERIC) AS value_sats,
    CAST(value AS BIGNUMERIC)
      - LAG(CAST(value AS BIGNUMERIC)) OVER (
          PARTITION BY transaction_hash
          ORDER BY `index`
        ) AS value_delta
  FROM `bigquery-public-data.crypto_bitcoin.outputs`
  WHERE block_timestamp >= TIMESTAMP('2013-01-01')
    AND block_timestamp < TIMESTAMP('2017-01-01')
),

summary AS (
  SELECT
    transaction_hash,
    ANY_VALUE(block_number) AS block_number,
    ANY_VALUE(block_timestamp) AS block_timestamp,
    COUNT(*) AS output_count,
    COUNTIF(output_index = 0 OR value_delta = 100000) AS matching_steps,
    SUM(value_sats) AS total_value
  FROM ordered
  GROUP BY transaction_hash
)

SELECT *
FROM summary
WHERE output_count >= 50
  AND matching_steps = output_count
ORDER BY output_count DESC, block_timestamp;
