package com.finalyear.pedestriannav;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.button.MaterialButton;
import com.google.android.material.switchmaterial.SwitchMaterial;
import com.google.android.material.textfield.TextInputEditText;

import java.util.Locale;

/**
 * Settings Activity for configuring app preferences
 */
public class SettingsActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "PedestrianNavPrefs";

    private TextInputEditText esp32IpInput;
    private SeekBar confidenceSeekBar;
    private TextView confidenceValue;
    private SeekBar cooldownSeekBar;
    private TextView cooldownValue;
    private SwitchMaterial voiceSwitch;
    private SwitchMaterial vibrationSwitch;
    private MaterialButton saveButton;

    private SharedPreferences preferences;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        // Enable back button
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        preferences = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);

        initializeViews();
        loadPreferences();
        setupListeners();
    }

    private void initializeViews() {
        esp32IpInput = findViewById(R.id.esp32IpInput);
        confidenceSeekBar = findViewById(R.id.confidenceSeekBar);
        confidenceValue = findViewById(R.id.confidenceValue);
        cooldownSeekBar = findViewById(R.id.cooldownSeekBar);
        cooldownValue = findViewById(R.id.cooldownValue);
        voiceSwitch = findViewById(R.id.voiceSwitch);
        vibrationSwitch = findViewById(R.id.vibrationSwitch);
        saveButton = findViewById(R.id.saveButton);
    }

    private void loadPreferences() {
        // ESP32 IP
        String ip = preferences.getString("esp32_ip", "192.168.1.100");
        esp32IpInput.setText(ip);

        // Confidence threshold (0.0 - 1.0, default 0.5)
        float confidence = preferences.getFloat("confidence_threshold", 0.5f);
        confidenceSeekBar.setProgress((int) (confidence * 100));
        confidenceValue.setText(String.format(Locale.US, "%.2f", confidence));

        // Alert cooldown (seconds, default 3)
        int cooldown = preferences.getInt("alert_cooldown", 3);
        cooldownSeekBar.setProgress(cooldown);
        cooldownValue.setText(cooldown + "s");

        // Voice alerts (default true)
        boolean voice = preferences.getBoolean("enable_voice", true);
        voiceSwitch.setChecked(voice);

        // Vibration (default true)
        boolean vibration = preferences.getBoolean("enable_vibration", true);
        vibrationSwitch.setChecked(vibration);
    }

    private void setupListeners() {
        // Confidence seek bar
        confidenceSeekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                float value = progress / 100f;
                confidenceValue.setText(String.format(Locale.US, "%.2f", value));
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        // Cooldown seek bar
        cooldownSeekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                cooldownValue.setText(progress + "s");
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        // Save button
        saveButton.setOnClickListener(v -> savePreferences());
    }

    private void savePreferences() {
        SharedPreferences.Editor editor = preferences.edit();

        // ESP32 IP
        String ip = esp32IpInput.getText().toString().trim();
        if (ip.isEmpty()) {
            Toast.makeText(this, "Please enter ESP32-CAM IP address",
                    Toast.LENGTH_SHORT).show();
            return;
        }
        editor.putString("esp32_ip", ip);

        // Confidence threshold
        float confidence = confidenceSeekBar.getProgress() / 100f;
        editor.putFloat("confidence_threshold", confidence);

        // Alert cooldown
        int cooldown = cooldownSeekBar.getProgress();
        editor.putInt("alert_cooldown", cooldown);

        // Voice alerts
        editor.putBoolean("enable_voice", voiceSwitch.isChecked());

        // Vibration
        editor.putBoolean("enable_vibration", vibrationSwitch.isChecked());

        // Save
        editor.apply();

        Toast.makeText(this, "Settings saved successfully",
                Toast.LENGTH_SHORT).show();
        finish();
    }

    @Override
    public boolean onSupportNavigateUp() {
        finish();
        return true;
    }
}
