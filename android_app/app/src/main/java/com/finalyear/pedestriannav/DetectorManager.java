package com.finalyear.pedestriannav;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.graphics.Bitmap;
import android.graphics.RectF;
import android.util.Log;

import org.tensorflow.lite.Interpreter;
import org.tensorflow.lite.gpu.CompatibilityList;
import org.tensorflow.lite.gpu.GpuDelegate;

import java.io.FileInputStream;
import java.io.IOException;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Manages TensorFlow Lite model for object detection
 * Handles model loading, inference, and post-processing
 */
public class DetectorManager {
    private static final String TAG = "DetectorManager";
    private static final String MODEL_FILE = "yolov8n_float16.tflite";
    private static final int INPUT_SIZE = 320;
    private static final float CONFIDENCE_THRESHOLD = 0.5f;
    private static final float NMS_THRESHOLD = 0.45f;

    private Interpreter tflite;
    private GpuDelegate gpuDelegate;
    private String[] labels;
    private boolean isGpuEnabled = false;

    public DetectorManager(Context context) {
        try {
            loadModel(context);
            loadLabels(context);
            Log.d(TAG, "Detector initialized successfully");
        } catch (Exception e) {
            Log.e(TAG, "Error initializing detector", e);
        }
    }

    private void loadModel(Context context) throws IOException {
        MappedByteBuffer modelBuffer = loadModelFile(context, MODEL_FILE);

        Interpreter.Options options = new Interpreter.Options();
        CompatibilityList compatList = new CompatibilityList();

        if (compatList.isDelegateSupportedOnThisDevice()) {
            GpuDelegate.Options delegateOptions = compatList.getBestOptionsForThisDevice();
            gpuDelegate = new GpuDelegate(delegateOptions);
            options.addDelegate(gpuDelegate);
            isGpuEnabled = true;
            Log.d(TAG, "GPU acceleration enabled");
        } else {
            options.setNumThreads(4);
            Log.d(TAG, "Using CPU with 4 threads");
        }

        tflite = new Interpreter(modelBuffer, options);
        Log.d(TAG, "Model loaded successfully");
    }

    private MappedByteBuffer loadModelFile(Context context, String filename) throws IOException {
        AssetFileDescriptor fileDescriptor = context.getAssets().openFd(filename);
        FileInputStream inputStream = new FileInputStream(fileDescriptor.getFileDescriptor());
        FileChannel fileChannel = inputStream.getChannel();
        long startOffset = fileDescriptor.getStartOffset();
        long declaredLength = fileDescriptor.getDeclaredLength();
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
    }

    private void loadLabels(Context context) {
        labels = CocoLabels.getLabels();
    }

    /**
     * Run object detection on a bitmap image
     */
    public List<Detection> detect(Bitmap bitmap) {
        if (tflite == null) {
            Log.e(TAG, "Detector not initialized");
            return new ArrayList<>();
        }

        try {
            // Resize image to model input size
            Bitmap resized = Bitmap.createScaledBitmap(bitmap, INPUT_SIZE, INPUT_SIZE, true);

            // Convert to float array
            float[][][][] input = bitmapToFloatArray(resized);

            // Prepare output tensors
            float[][][] outputBoxes = new float[1][2100][4];
            float[][][] outputScores = new float[1][2100][80];

            // Run inference
            Map<Integer, Object> outputs = new HashMap<>();
            outputs.put(0, outputBoxes);
            outputs.put(1, outputScores);

            tflite.runForMultipleInputsOutputs(new Object[]{input}, outputs);

            // Post-process results
            List<Detection> detections = postProcess(
                    outputBoxes[0],
                    outputScores[0],
                    bitmap.getWidth(),
                    bitmap.getHeight()
            );

            return detections;

        } catch (Exception e) {
            Log.e(TAG, "Error during detection", e);
            return new ArrayList<>();
        }
    }

    private float[][][][] bitmapToFloatArray(Bitmap bitmap) {
        float[][][][] input = new float[1][INPUT_SIZE][INPUT_SIZE][3];
        int[] pixels = new int[INPUT_SIZE * INPUT_SIZE];
        bitmap.getPixels(pixels, 0, INPUT_SIZE, 0, 0, INPUT_SIZE, INPUT_SIZE);

        for (int y = 0; y < INPUT_SIZE; y++) {
            for (int x = 0; x < INPUT_SIZE; x++) {
                int pixel = pixels[y * INPUT_SIZE + x];
                input[0][y][x][0] = ((pixel >> 16) & 0xFF) / 255.0f;  // R
                input[0][y][x][1] = ((pixel >> 8) & 0xFF) / 255.0f;   // G
                input[0][y][x][2] = (pixel & 0xFF) / 255.0f;          // B
            }
        }
        return input;
    }

    private List<Detection> postProcess(float[][] boxes, float[][] scores,
                                         int imageWidth, int imageHeight) {
        List<Detection> detections = new ArrayList<>();

        for (int i = 0; i < boxes.length; i++) {
            // Find max class score
            float maxScore = 0;
            int classId = -1;
            for (int j = 0; j < scores[i].length; j++) {
                if (scores[i][j] > maxScore) {
                    maxScore = scores[i][j];
                    classId = j;
                }
            }

            if (maxScore > CONFIDENCE_THRESHOLD && classId >= 0 && classId < labels.length) {
                // Scale box coordinates to image size
                float x1 = boxes[i][0] * imageWidth;
                float y1 = boxes[i][1] * imageHeight;
                float x2 = boxes[i][2] * imageWidth;
                float y2 = boxes[i][3] * imageHeight;

                RectF box = new RectF(x1, y1, x2, y2);
                String className = labels[classId];

                Detection detection = new Detection(box, className, classId, maxScore);
                detections.add(detection);
            }
        }

        // Apply Non-Maximum Suppression
        return applyNMS(detections, NMS_THRESHOLD);
    }

    private List<Detection> applyNMS(List<Detection> detections, float nmsThreshold) {
        if (detections.isEmpty()) return detections;

        // Sort by confidence (descending)
        detections.sort((d1, d2) -> Float.compare(d2.getConfidence(), d1.getConfidence()));

        List<Detection> result = new ArrayList<>();
        boolean[] suppressed = new boolean[detections.size()];

        for (int i = 0; i < detections.size(); i++) {
            if (suppressed[i]) continue;

            Detection current = detections.get(i);
            result.add(current);

            for (int j = i + 1; j < detections.size(); j++) {
                if (suppressed[j]) continue;

                Detection candidate = detections.get(j);
                if (current.getClassId() == candidate.getClassId()) {
                    float iou = calculateIoU(current.getBox(), candidate.getBox());
                    if (iou > nmsThreshold) {
                        suppressed[j] = true;
                    }
                }
            }
        }

        return result;
    }

    private float calculateIoU(RectF box1, RectF box2) {
        float intersectionLeft = Math.max(box1.left, box2.left);
        float intersectionTop = Math.max(box1.top, box2.top);
        float intersectionRight = Math.min(box1.right, box2.right);
        float intersectionBottom = Math.min(box1.bottom, box2.bottom);

        if (intersectionRight < intersectionLeft || intersectionBottom < intersectionTop) {
            return 0.0f;
        }

        float intersectionArea = (intersectionRight - intersectionLeft) *
                (intersectionBottom - intersectionTop);
        float box1Area = box1.width() * box1.height();
        float box2Area = box2.width() * box2.height();
        float unionArea = box1Area + box2Area - intersectionArea;

        return intersectionArea / unionArea;
    }

    public boolean isGpuEnabled() {
        return isGpuEnabled;
    }

    public void close() {
        if (tflite != null) {
            tflite.close();
            tflite = null;
        }
        if (gpuDelegate != null) {
            gpuDelegate.close();
            gpuDelegate = null;
        }
    }
}
