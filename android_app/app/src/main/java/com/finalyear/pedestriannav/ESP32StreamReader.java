package com.finalyear.pedestriannav;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

/**
 * Reads MJPEG stream from ESP32-CAM
 */
public class ESP32StreamReader {
    private static final String TAG = "ESP32StreamReader";
    private static final int JPEG_START = 0xFFD8;
    private static final int JPEG_END = 0xFFD9;

    private String esp32Ip;
    private OkHttpClient client;
    private boolean isRunning = false;
    private ExecutorService executorService;
    private Call currentCall;

    public interface FrameCallback {
        void onFrame(Bitmap frame);
        void onError(String error);
        void onConnected();
    }

    public ESP32StreamReader(String esp32Ip) {
        this.esp32Ip = esp32Ip;
        this.executorService = Executors.newSingleThreadExecutor();
        this.client = new OkHttpClient.Builder()
                .readTimeout(0, java.util.concurrent.TimeUnit.MILLISECONDS)
                .build();
    }

    public void setEsp32Ip(String ip) {
        this.esp32Ip = ip;
    }

    public void startStream(FrameCallback callback) {
        if (isRunning) {
            Log.w(TAG, "Stream already running");
            return;
        }

        isRunning = true;
        String streamUrl = "http://" + esp32Ip + ":81/stream";
        Log.d(TAG, "Starting stream from: " + streamUrl);

        executorService.execute(() -> {
            try {
                Request request = new Request.Builder()
                        .url(streamUrl)
                        .build();

                currentCall = client.newCall(request);
                currentCall.enqueue(new Callback() {
                    @Override
                    public void onFailure(Call call, IOException e) {
                        if (isRunning) {
                            callback.onError("Connection failed: " + e.getMessage());
                            isRunning = false;
                        }
                    }

                    @Override
                    public void onResponse(Call call, Response response) throws IOException {
                        if (!response.isSuccessful()) {
                            callback.onError("HTTP error: " + response.code());
                            return;
                        }

                        callback.onConnected();
                        Log.d(TAG, "Connected to ESP32-CAM");

                        try (InputStream inputStream = response.body().byteStream()) {
                            readMjpegStream(inputStream, callback);
                        } catch (Exception e) {
                            if (isRunning) {
                                callback.onError("Stream error: " + e.getMessage());
                            }
                        }
                    }
                });

            } catch (Exception e) {
                callback.onError("Failed to start stream: " + e.getMessage());
                isRunning = false;
            }
        });
    }

    private void readMjpegStream(InputStream inputStream, FrameCallback callback) throws IOException {
        ByteArrayOutputStream jpegData = new ByteArrayOutputStream();
        boolean inJpeg = false;
        int prev = 0;
        int current;

        while (isRunning && (current = inputStream.read()) != -1) {
            // Detect JPEG start marker (0xFFD8)
            if (prev == 0xFF && current == 0xD8) {
                inJpeg = true;
                jpegData.reset();
                jpegData.write(0xFF);
                jpegData.write(0xD8);
            }
            // Detect JPEG end marker (0xFFD9)
            else if (prev == 0xFF && current == 0xD9 && inJpeg) {
                jpegData.write(0xFF);
                jpegData.write(0xD9);
                inJpeg = false;

                // Decode JPEG
                byte[] frameData = jpegData.toByteArray();
                Bitmap frame = BitmapFactory.decodeByteArray(frameData, 0, frameData.length);
                
                if (frame != null) {
                    callback.onFrame(frame);
                } else {
                    Log.w(TAG, "Failed to decode JPEG frame");
                }
            }
            // Collect JPEG data
            else if (inJpeg) {
                jpegData.write(current);
            }

            prev = current;
        }

        Log.d(TAG, "Stream reading stopped");
    }

    public void stopStream() {
        isRunning = false;
        if (currentCall != null) {
            currentCall.cancel();
        }
        Log.d(TAG, "Stream stopped");
    }

    public void shutdown() {
        stopStream();
        if (executorService != null) {
            executorService.shutdownNow();
        }
    }
}
