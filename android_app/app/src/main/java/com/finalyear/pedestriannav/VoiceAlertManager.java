package com.finalyear.pedestriannav;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.speech.tts.TextToSpeech;
import android.util.Log;

import java.util.Locale;

/**
 * Manages voice alerts and haptic feedback
 */
public class VoiceAlertManager {
    private static final String TAG = "VoiceAlertManager";
    private static final long ALERT_COOLDOWN = 3000; // 3 seconds

    private TextToSpeech tts;
    private Vibrator vibrator;
    private SharedPreferences preferences;
    private Context context;
    private long lastAlertTime = 0;
    private String lastAlertClass = "";

    public VoiceAlertManager(Context context, SharedPreferences preferences) {
        this.context = context;
        this.preferences = preferences;
        
        initializeTTS();
        initializeVibrator();
    }

    private void initializeTTS() {
        tts = new TextToSpeech(context, status -> {
            if (status == TextToSpeech.SUCCESS) {
                int result = tts.setLanguage(Locale.US);
                if (result == TextToSpeech.LANG_MISSING_DATA ||
                        result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    Log.e(TAG, "Language not supported");
                } else {
                    tts.setSpeechRate(1.1f);
                    tts.setPitch(1.0f);
                    Log.d(TAG, "TTS initialized successfully");
                }
            } else {
                Log.e(TAG, "TTS initialization failed");
            }
        });
    }

    private void initializeVibrator() {
        vibrator = (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
    }

    public void alert(Detection detection) {
        long now = System.currentTimeMillis();
        long cooldown = preferences.getInt("alert_cooldown", 3) * 1000;

        // Check cooldown
        if (now - lastAlertTime < cooldown &&
                detection.getClassName().equals(lastAlertClass)) {
            return; // Don't spam same object
        }

        lastAlertTime = now;
        lastAlertClass = detection.getClassName();

        // Voice alert
        if (preferences.getBoolean("enable_voice", true)) {
            String message = generateAlertMessage(detection);
            speak(message);
        }

        // Vibration
        if (preferences.getBoolean("enable_vibration", true)) {
            vibrate(detection);
        }

        Log.d(TAG, "Alert: " + detection.toString());
    }

    private String generateAlertMessage(Detection detection) {
        String className = detection.getClassName();
        float distance = detection.getDistance();
        float confidence = detection.getConfidence();

        // High urgency (very close)
        if (distance < 1.5f) {
            return getUrgentMessage(className);
        }
        // Medium urgency (close)
        else if (distance < 3.0f) {
            return getCautionMessage(className, distance);
        }
        // Low urgency (detected)
        else {
            return getInfoMessage(className, distance);
        }
    }

    private String getUrgentMessage(String className) {
        switch (className.toLowerCase()) {
            case "person":
                return "Warning! Person very close!";
            case "car":
            case "truck":
            case "bus":
                return "Danger! Vehicle approaching!";
            case "bicycle":
            case "motorcycle":
                return "Watch out! Bicycle approaching!";
            case "dog":
            case "cat":
                return "Animal nearby!";
            case "chair":
            case "couch":
                return "Obstacle ahead!";
            default:
                return "Warning! " + className + " ahead!";
        }
    }

    private String getCautionMessage(String className, float distance) {
        return String.format("Caution. %s at %.1f meters.", className, distance);
    }

    private String getInfoMessage(String className, float distance) {
        return String.format("%s detected at %.1f meters.", className, distance);
    }

    private void speak(String message) {
        if (tts != null) {
            tts.speak(message, TextToSpeech.QUEUE_FLUSH, null, null);
        }
    }

    private void vibrate(Detection detection) {
        if (vibrator == null || !vibrator.hasVibrator()) {
            return;
        }

        long[] pattern = getVibrationPattern(detection.getDistance());

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            VibrationEffect effect = VibrationEffect.createWaveform(pattern, -1);
            vibrator.vibrate(effect);
        } else {
            vibrator.vibrate(pattern, -1);
        }
    }

    private long[] getVibrationPattern(float distance) {
        if (distance < 1.5f) {
            // Urgent: 3 short bursts
            return new long[]{0, 150, 100, 150, 100, 150};
        } else if (distance < 3.0f) {
            // Caution: 2 medium bursts
            return new long[]{0, 200, 150, 200};
        } else {
            // Info: 1 long burst
            return new long[]{0, 300};
        }
    }

    public void testAlert() {
        speak("Test alert. System is working correctly.");
        if (vibrator != null && vibrator.hasVibrator()) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                vibrator.vibrate(VibrationEffect.createOneShot(500,
                        VibrationEffect.DEFAULT_AMPLITUDE));
            } else {
                vibrator.vibrate(500);
            }
        }
    }

    public void shutdown() {
        if (tts != null) {
            tts.stop();
            tts.shutdown();
            tts = null;
        }
    }
}
