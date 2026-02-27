package com.finalyear.pedestriannav;

import android.Manifest;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.button.MaterialButton;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Main Activity for Pedestrian Navigator
 * Handles UI, camera stream, detection display
 */
public class MainActivity extends AppCompatActivity {

    private static final int PERMISSION_REQUEST_CODE = 100;
    private static final String PREFS_NAME = "PedestrianNavPrefs";

    // UI Components
    private ImageView imagePreview;
    private DetectionOverlay detectionOverlay;
    private View statusIndicator;
    private TextView statusText;
    private TextView fpsText;
    private TextView latencyText;
    private TextView detectionsText;
    private MaterialButton controlButton;
    private RecyclerView detectionsRecyclerView;

    // Core Components
    private DetectorManager detectorManager;
    private ESP32StreamReader streamReader;
    private VoiceAlertManager voiceAlertManager;
    private DetectionAdapter detectionAdapter;

    // State
    private boolean isDetecting = false;
    private SharedPreferences preferences;
    private Handler uiHandler;

    // Stats
    private long frameCount = 0;
    private long startTime = 0;
    private List<DetectionItem> recentDetections = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initializeUI();
        initializeComponents();
        checkPermissions();
    }

    private void initializeUI() {
        imagePreview = findViewById(R.id.imagePreview);
        detectionOverlay = findViewById(R.id.detectionOverlay);
        statusIndicator = findViewById(R.id.statusIndicator);
        statusText = findViewById(R.id.statusText);
        fpsText = findViewById(R.id.fpsText);
        latencyText = findViewById(R.id.latencyText);
        detectionsText = findViewById(R.id.detectionsText);
        controlButton = findViewById(R.id.controlButton);
        detectionsRecyclerView = findViewById(R.id.detectionsRecyclerView);

        // Setup RecyclerView
        detectionAdapter = new DetectionAdapter(recentDetections);
        detectionsRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        detectionsRecyclerView.setAdapter(detectionAdapter);

        // Control button
        controlButton.setOnClickListener(v -> {
            if (isDetecting) {
                stopDetection();
            } else {
                startDetection();
            }
        });

        // Settings button
        findViewById(R.id.settingsButton).setOnClickListener(v -> {
            startActivity(new Intent(MainActivity.this, SettingsActivity.class));
        });

        uiHandler = new Handler(Looper.getMainLooper());
    }

    private void initializeComponents() {
        preferences = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);

        // Initialize detector
        detectorManager = new DetectorManager(this);

        // Initialize voice alerts
        voiceAlertManager = new VoiceAlertManager(this, preferences);

        // Initialize stream reader
        String esp32Ip = preferences.getString("esp32_ip", "192.168.1.100");
        streamReader = new ESP32StreamReader(esp32Ip);
    }

    private void checkPermissions() {
        String[] permissions = {
                Manifest.permission.INTERNET,
                Manifest.permission.ACCESS_NETWORK_STATE,
                Manifest.permission.BLUETOOTH_CONNECT,
                Manifest.permission.VIBRATE
        };

        List<String> permissionsToRequest = new ArrayList<>();
        for (String permission : permissions) {
            if (ContextCompat.checkSelfPermission(this, permission)
                    != PackageManager.PERMISSION_GRANTED) {
                permissionsToRequest.add(permission);
            }
        }

        if (!permissionsToRequest.isEmpty()) {
            ActivityCompat.requestPermissions(this,
                    permissionsToRequest.toArray(new String[0]),
                    PERMISSION_REQUEST_CODE);
        }
    }

    private void startDetection() {
        updateStatus(StatusState.CONNECTING);
        statusText.setText(R.string.status_connecting);

        startTime = System.currentTimeMillis();
        frameCount = 0;

        streamReader.startStream(new ESP32StreamReader.FrameCallback() {
            @Override
            public void onFrame(Bitmap frame) {
                uiHandler.post(() -> processFrame(frame));
            }

            @Override
            public void onError(String error) {
                uiHandler.post(() -> {
                    updateStatus(StatusState.DISCONNECTED);
                    statusText.setText("Error: " + error);
                    Toast.makeText(MainActivity.this,
                            "Connection failed. Check ESP32-CAM WiFi.",
                            Toast.LENGTH_LONG).show();
                    stopDetection();
                });
            }

            @Override
            public void onConnected() {
                uiHandler.post(() -> {
                    updateStatus(StatusState.DETECTING);
                    statusText.setText(R.string.status_detecting);
                });
            }
        });

        isDetecting = true;
        controlButton.setText(R.string.stop_detection);
        controlButton.setBackgroundColor(getColor(R.color.status_disconnected));
    }

    private void stopDetection() {
        if (streamReader != null) {
            streamReader.stopStream();
        }

        isDetecting = false;
        updateStatus(StatusState.DISCONNECTED);
        statusText.setText(R.string.status_disconnected);
        controlButton.setText(R.string.start_detection);
        controlButton.setBackgroundColor(getColor(R.color.primary));
    }

    private void processFrame(Bitmap frame) {
        if (!isDetecting) return;

        // Display frame
        imagePreview.setImageBitmap(frame);

        // Run detection
        long inferenceStart = System.currentTimeMillis();
        List<Detection> detections = detectorManager.detect(frame);
        long inferenceTime = System.currentTimeMillis() - inferenceStart;

        // Update overlay
        detectionOverlay.setDetections(detections, frame.getWidth(), frame.getHeight());

        // Update stats
        frameCount++;
        updateStats(inferenceTime, detections.size());

        // Process alerts
        float confidenceThreshold = preferences.getFloat("confidence_threshold", 0.5f);
        for (Detection detection : detections) {
            if (detection.getConfidence() >= confidenceThreshold && isImportant(detection)) {
                voiceAlertManager.alert(detection);
                addRecentDetection(detection);
            }
        }
    }

    private void updateStats(long inferenceTime, int detectionCount) {
        // Update FPS
        long elapsed = System.currentTimeMillis() - startTime;
        if (elapsed > 0) {
            float fps = (frameCount * 1000f) / elapsed;
            fpsText.setText(String.format(Locale.US, "FPS: %.1f", fps));
        }

        // Update latency
        latencyText.setText(String.format(Locale.US, "Latency: %dms", inferenceTime));

        // Update detection count
        detectionsText.setText(String.format(Locale.US, "Detections: %d", detectionCount));
    }

    private void updateStatus(StatusState state) {
        int color;
        switch (state) {
            case CONNECTED:
                color = getColor(R.color.status_connected);
                break;
            case DETECTING:
                color = getColor(R.color.status_detecting);
                break;
            default:
                color = getColor(R.color.status_disconnected);
        }
        statusIndicator.setBackgroundTintList(android.content.res.ColorStateList.valueOf(color));
    }

    private boolean isImportant(Detection detection) {
        String[] importantClasses = {
                "person", "bicycle", "car", "motorcycle", "bus", "truck",
                "traffic light", "stop sign", "dog", "cat", "chair", "couch"
        };
        String className = detection.getClassName().toLowerCase();
        for (String important : importantClasses) {
            if (className.equals(important)) {
                return true;
            }
        }
        return false;
    }

    private void addRecentDetection(Detection detection) {
        DetectionItem item = new DetectionItem(
                detection.getClassName(),
                detection.getConfidence(),
                detection.getDistance(),
                System.currentTimeMillis()
        );

        recentDetections.add(0, item);
        if (recentDetections.size() > 20) {
            recentDetections.remove(recentDetections.size() - 1);
        }

        detectionAdapter.notifyDataSetChanged();

        // Scroll to top
        detectionsRecyclerView.smoothScrollToPosition(0);
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Reload preferences
        String esp32Ip = preferences.getString("esp32_ip", "192.168.1.100");
        if (streamReader != null) {
            streamReader.setEsp32Ip(esp32Ip);
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (isDetecting) {
            stopDetection();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (detectorManager != null) {
            detectorManager.close();
        }
        if (voiceAlertManager != null) {
            voiceAlertManager.shutdown();
        }
        if (streamReader != null) {
            streamReader.stopStream();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CODE) {
            boolean allGranted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }
            if (!allGranted) {
                Toast.makeText(this, "Permissions required for app to function",
                        Toast.LENGTH_LONG).show();
            }
        }
    }

    enum StatusState {
        DISCONNECTED, CONNECTING, CONNECTED, DETECTING
    }
}
