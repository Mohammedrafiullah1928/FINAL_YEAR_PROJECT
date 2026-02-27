package com.finalyear.pedestriannav;

import android.graphics.RectF;

/**
 * Represents a detected object
 */
public class Detection {
    private final RectF box;
    private final String className;
    private final int classId;
    private final float confidence;
    private float distance;

    public Detection(RectF box, String className, int classId, float confidence) {
        this.box = box;
        this.className = className;
        this.classId = classId;
        this.confidence = confidence;
        this.distance = estimateDistance();
    }

    private float estimateDistance() {
        // Rough distance estimation based on bounding box size
        // Assumes person height ~1.7m, camera FOV ~60 degrees
        // This is approximate and should be calibrated for your setup
        float imageHeight = 480f; // Assuming VGA
        float boxHeight = box.height();
        
        if (boxHeight > 0) {
            // Simple inverse proportion: larger box = closer object
            float distanceMeters = (imageHeight / boxHeight) * 0.5f;
            return Math.max(0.5f, Math.min(distanceMeters, 10.0f));
        }
        return 5.0f; // Default
    }

    public RectF getBox() {
        return box;
    }

    public String getClassName() {
        return className;
    }

    public int getClassId() {
        return classId;
    }

    public float getConfidence() {
        return confidence;
    }

    public float getDistance() {
        return distance;
    }

    public void setDistance(float distance) {
        this.distance = distance;
    }

    @Override
    public String toString() {
        return String.format("%s (%.2f) at %.1fm", className, confidence, distance);
    }
}
