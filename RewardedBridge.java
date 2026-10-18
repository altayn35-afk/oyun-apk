package org.minikkasifler.ads;

import android.app.Activity;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.MobileAds;
import com.google.android.gms.ads.RequestConfiguration;
import com.google.android.gms.ads.rewarded.RewardedAd;
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback;
import com.google.android.gms.ads.FullScreenContentCallback;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.AdError;
import com.google.android.gms.ads.rewarded.RewardItem;
import java.util.Collections;

public final class RewardedBridge {
    private static volatile RewardedAd loaded;
    private static volatile String event = "";
    private static volatile boolean earned = false;
    private static String adUnit;
    private static boolean loading = false;

    public static void initialize(final Activity activity, final String unit) {
        adUnit = unit;
        activity.runOnUiThread(() -> {
            RequestConfiguration configuration = new RequestConfiguration.Builder()
                .setTagForChildDirectedTreatment(RequestConfiguration.TAG_FOR_CHILD_DIRECTED_TREATMENT_TRUE)
                .setTagForUnderAgeOfConsent(RequestConfiguration.TAG_FOR_UNDER_AGE_OF_CONSENT_TRUE)
                .setMaxAdContentRating(RequestConfiguration.MAX_AD_CONTENT_RATING_G)
                .build();
            MobileAds.setRequestConfiguration(configuration);
            MobileAds.initialize(activity, status -> load(activity));
        });
    }

    private static void load(final Activity activity) {
        if (loading || loaded != null || adUnit == null) return;
        loading = true;
        RewardedAd.load(activity, adUnit, new AdRequest.Builder().build(),
            new RewardedAdLoadCallback() {
                @Override public void onAdLoaded(RewardedAd ad) {
                    loaded = ad;
                    loading = false;
                }
                @Override public void onAdFailedToLoad(LoadAdError error) {
                    loaded = null;
                    loading = false;
                }
            });
    }

    public static boolean show(final Activity activity) {
        if (loaded == null) {
            activity.runOnUiThread(() -> load(activity));
            return false;
        }
        activity.runOnUiThread(() -> {
            final RewardedAd ad = loaded;
            loaded = null;
            if (ad == null) { event = "failed"; return; }
            earned = false;
            ad.setFullScreenContentCallback(new FullScreenContentCallback() {
                @Override public void onAdDismissedFullScreenContent() {
                    if (!earned) event = "closed";
                    load(activity);
                }
                @Override public void onAdFailedToShowFullScreenContent(AdError error) {
                    event = "failed";
                    load(activity);
                }
            });
            ad.show(activity, rewardItem -> { earned = true; event = "earned"; });
        });
        return true;
    }

    public static synchronized String consumeEvent() {
        String value = event;
        event = "";
        return value;
    }
}
