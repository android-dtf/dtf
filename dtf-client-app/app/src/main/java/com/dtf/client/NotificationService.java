package com.dtf.client;

import android.app.IntentService;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Build;
import android.support.v4.app.NotificationCompat;
import android.util.Log;


public class NotificationService extends IntentService {

    NotificationManager notificationManager;
    private static final int NOTIFICATION_ID = 1;
    private static final String TAG = "NotificationService";

    public NotificationService() {
        super("NotificationService");
    }

    @Override
    protected void onHandleIntent(Intent intent) {
        stickyNotification();
    }

    private void stickyNotification() {

        Log.d(TAG, "Creating our sticky notification!");

        notificationManager =
                (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);

        Intent i = new Intent();
        i.setAction(android.provider.Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
        i.setData(Uri.parse("package:com.dtf.client"));

        PendingIntent pendingIntent = PendingIntent.getActivity(this,
                NOTIFICATION_ID, i, PendingIntent.FLAG_UPDATE_CURRENT);

        Notification n;

        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.JELLY_BEAN) {

            NotificationCompat.Builder builder = new NotificationCompat.Builder(this)
                    .setContentTitle("dtfClient is Installed!")
                    .setContentText("Click here to uninstall")
                    .setContentIntent(pendingIntent)
                    .setSmallIcon(R.drawable.ic_build_white_48dp)
                    .setLargeIcon(BitmapFactory.decodeResource(getResources(), R.drawable.ic_launcher));

            n = builder.build();
        } else {

            Notification.Builder builder = new Notification.Builder(this)
                    .setContentTitle("dtfClient is Installed!")
                    .setContentText("Click here to uninstall")
                    .setContentIntent(pendingIntent)
                    .setSmallIcon(R.drawable.ic_build_white_48dp)
                    .setLargeIcon(BitmapFactory.decodeResource(getResources(), R.drawable.ic_launcher));
            n = builder.build();
        }

        n.flags |= Notification.FLAG_NO_CLEAR | Notification.FLAG_ONGOING_EVENT;
        notificationManager.notify(NOTIFICATION_ID, n);
    }
}
