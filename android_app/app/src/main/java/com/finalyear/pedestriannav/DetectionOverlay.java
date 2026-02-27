package com.finalyear.pedestriannav;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.View;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Custom view to draw detection bounding boxes over camera preview
 */
public class DetectionOverlay extends View {
    private List<Detection> detections = new ArrayList<>();
    private Paint boxPaint;
    private Paint textPaint;
    private Paint backgroundPaint;
    private int imageWidth = 1;
    private int imageHeight = 1;

    public DetectionOverlay(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    private void init() {
        // Box paint
        boxPaint = new Paint();
        boxPaint.setStyle(Paint.Style.STROKE);
        boxPaint.setStrokeWidth(4f);
        boxPaint.setColor(Color.GREEN);

        // Text paint
        textPaint = new Paint();
        textPaint.setColor(Color.WHITE);
        textPaint.setTextSize(32f);
        textPaint.setStyle(Paint.Style.FILL);
        textPaint.setAntiAlias(true);

        // Background paint for text
        backgroundPaint = new Paint();
        backgroundPaint.setColor(Color.argb(180, 0, 0, 0));
        backgroundPaint.setStyle(Paint.Style.FILL);
    }

    public void setDetections(List<Detection> detections, int imageWidth, int imageHeight) {
        this.detections = new ArrayList<>(detections);
        this.imageWidth = imageWidth;
        this.imageHeight = imageHeight;
        invalidate(); // Trigger redraw
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        if (detections == null || detections.isEmpty()) {
            return;
        }

        // Calculate scale factors
        float scaleX = (float) getWidth() / imageWidth;
        float scaleY = (float) getHeight() / imageHeight;

        for (Detection detection : detections) {
            RectF box = detection.getBox();

            // Scale box to view size
            RectF scaledBox = new RectF(
                    box.left * scaleX,
                    box.top * scaleY,
                    box.right * scaleX,
                    box.bottom * scaleY
            );

            // Choose color based on distance
            int color = getColorForDistance(detection.getDistance());
            boxPaint.setColor(color);

            // Draw bounding box
            canvas.drawRect(scaledBox, boxPaint);

            // Draw label
            String label = String.format(Locale.US, "%s %.0f%% (%.1fm)",
                    detection.getClassName(),
                    detection.getConfidence() * 100,
                    detection.getDistance());

            // Measure text
            float textWidth = textPaint.measureText(label);
            float textHeight = textPaint.getTextSize();

            // Draw text background
            float labelX = scaledBox.left;
            float labelY = scaledBox.top - textHeight - 8;
            if (labelY < 0) {
                labelY = scaledBox.top + textHeight + 8;
            }

            RectF textBackground = new RectF(
                    labelX,
                    labelY - textHeight - 4,
                    labelX + textWidth + 8,
                    labelY + 4
            );
            canvas.drawRect(textBackground, backgroundPaint);

            // Draw text
            canvas.drawText(label, labelX + 4, labelY, textPaint);
        }
    }

    private int getColorForDistance(float distance) {
        if (distance < 1.5f) {
            return Color.RED; // Danger
        } else if (distance < 3.0f) {
            return Color.YELLOW; // Caution
        } else {
            return Color.GREEN; // Safe
        }
    }
}
