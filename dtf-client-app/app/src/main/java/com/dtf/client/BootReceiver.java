package com.dtf.client;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class BootReceiver extends BroadcastReceiver {

    public BootReceiver() {
    }

    @Override
    public void onReceive(Context context, Intent intent) {

        if(intent.getAction().equals("android.intent.action.BOOT_COMPLETED")) {

            /* Start the notification banner */
            context.startService(new Intent(context, NotificationService.class));

            /* Start the LocalSocketServer */
            context.startService(new Intent(context, SocketService.class));
        }

    }
}
