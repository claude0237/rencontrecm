-- Add premiere_periode_decouverte field to user_subscription table
-- This field tracks if the subscription is the first discovery period with full benefits

ALTER TABLE user_subscription ADD COLUMN premiere_periode_decouverte BOOLEAN DEFAULT FALSE;
