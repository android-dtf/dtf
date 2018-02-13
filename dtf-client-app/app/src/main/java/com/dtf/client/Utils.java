package com.dtf.client;


import android.os.Build;

public class Utils {

    static String cpu = Build.CPU_ABI;

    static boolean isIntel() {

        if (cpu.startsWith("x86")) {
            return true;
        }
        return false;
    }

    static boolean isArm() {

        if (cpu.startsWith("arm")) {
            return true;
        }
        return false;
    }
}
