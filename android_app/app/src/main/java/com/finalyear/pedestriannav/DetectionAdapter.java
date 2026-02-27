package com.finalyear.pedestriannav;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;

/**
 * Adapter for displaying recent detections in RecyclerView
 */
public class DetectionAdapter extends RecyclerView.Adapter<DetectionAdapter.DetectionViewHolder> {

    private final List<DetectionItem> detections;

    public DetectionAdapter(List<DetectionItem> detections) {
        this.detections = detections;
    }

    @NonNull
    @Override
    public DetectionViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_detection, parent, false);
        return new DetectionViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull DetectionViewHolder holder, int position) {
        DetectionItem item = detections.get(position);
        holder.bind(item);
    }

    @Override
    public int getItemCount() {
        return detections.size();
    }

    static class DetectionViewHolder extends RecyclerView.ViewHolder {
        private final TextView nameText;
        private final TextView detailsText;
        private final TextView timeText;

        public DetectionViewHolder(@NonNull View itemView) {
            super(itemView);
            nameText = itemView.findViewById(R.id.detectionName);
            detailsText = itemView.findViewById(R.id.detectionDetails);
            timeText = itemView.findViewById(R.id.detectionTime);
        }

        public void bind(DetectionItem item) {
            nameText.setText(item.getName());
            detailsText.setText(item.getDetails());
            timeText.setText(item.getTimeAgo());
        }
    }
}
