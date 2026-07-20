-- Strict fingerprint: 256 outputs, value[i] = (i+1)*100000 sats, sum = 3289600000
-- Expected: at least Puzzle TX 08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15

WITH candidate_outputs AS (
  SELECT
    transaction_hash,
    block_number,
    block_timestamp,
    `index` AS output_index,
    CAST(value AS BIGNUMERIC) AS value_sats
  FROM `bigquery-public-data.crypto_bitcoin.outputs`
  WHERE block_timestamp >= TIMESTAMP('2014-01-01')
    AND block_timestamp < TIMESTAMP('2016-01-01')
),

grouped AS (
  SELECT
    transaction_hash,
    ANY_VALUE(block_number) AS block_number,
    ANY_VALUE(block_timestamp) AS block_timestamp,
    COUNT(*) AS output_count,
    COUNTIF(
      value_sats = CAST((output_index + 1) * 100000 AS BIGNUMERIC)
    ) AS exact_position_matches,
    SUM(value_sats) AS output_sum
  FROM candidate_outputs
  GROUP BY transaction_hash
)

SELECT
  transaction_hash,
  block_number,
  block_timestamp,
  output_count,
  exact_position_matches,
  output_sum
FROM grouped
WHERE output_count = 256
  AND exact_position_matches = 256
  AND output_sum = CAST(3289600000 AS BIGNUMERIC)
ORDER BY block_timestamp;
