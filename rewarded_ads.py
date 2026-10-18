"""Android rewarded-ad bridge. Never awards a life merely for opening an ad."""
from kivy.utils import platform

TEST_AD_UNIT = "ca-app-pub-3940256099942544/5224354917"

class RewardedAds:
    def __init__(self):
        self.bridge = None
        self.activity = None

    def initialize(self):
        if platform != 'android':
            return
        try:
            from jnius import autoclass
            self.activity = autoclass('org.kivy.android.PythonActivity').mActivity
            self.bridge = autoclass('org.minikkasifler.ads.RewardedBridge')
            self.bridge.initialize(self.activity, TEST_AD_UNIT)
        except Exception as exc:
            print('Rewarded ads initialization:', exc)

    def show(self):
        if self.bridge is None:
            return False
        try:
            return bool(self.bridge.show(self.activity))
        except Exception as exc:
            print('Rewarded ads show:', exc)
            return False

    def poll(self):
        if self.bridge is None:
            return None
        try:
            value = str(self.bridge.consumeEvent())
            return value if value in ('earned', 'closed', 'failed') else None
        except Exception:
            return None
