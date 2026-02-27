package com.finalyear.pedestriannav;

/**
 * Detection item for RecyclerView
 */
public class DetectionItem {
    private final String name;
    private final float confidence;
    private final float distance;
    private final long timestamp;

    public DetectionItem(String name, float confidence, float distance, long timestamp) {
        this.name = name;
        this.confidence = confidence;
        this.distance = distance;
        this.timestamp = timestamp;
    }

    public String getName() {
        return name;
    }

    public float getConfidence() {
        return confidence;
    }

    public float getDistance() {
        return distance;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public String getTimeAgo() {
        long diff = System.currentTimeMillis() - timestamp;
        long seconds = diff / 1000;
        
        if (seconds < 60) {
            return seconds + "s ago";
        } else if (seconds < 3600) {
            return (seconds / 60) + "m ago";
        } else {
            return (seconds / 3600) + "h ago";
        }
    }

    public String getDetails() {
        return String.format("Distance: %.1fm • Confidence: %.0f%%",
                distance, confidence * 100);
    }
}
