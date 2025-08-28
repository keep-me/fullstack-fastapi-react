import FingerprintJS from "@fingerprintjs/fingerprintjs";
import {
  FINGERPRINT_GENERATION_DELAY,
  DEFAULT_FINGERPRINT_PREFIX,
  STORAGE_KEYS,
} from "@/config/env";

export const getFingerprint = async (): Promise<string> => {
  try {
    let fingerprint = localStorage.getItem(STORAGE_KEYS.FINGERPRINT);

    if (fingerprint) {
      return fingerprint;
    }

    return new Promise((resolve) => {
      setTimeout(async () => {
        try {
          const fp = await FingerprintJS.load();
          const { visitorId } = await fp.get();
          fingerprint = visitorId;
          localStorage.setItem(STORAGE_KEYS.FINGERPRINT, fingerprint);
          resolve(fingerprint);
        } catch (error) {
          console.error("Error creating fingerprint:", error);
          const defaultFingerprint = DEFAULT_FINGERPRINT_PREFIX + Date.now();
          localStorage.setItem(STORAGE_KEYS.FINGERPRINT, defaultFingerprint);
          resolve(defaultFingerprint);
        }
      }, FINGERPRINT_GENERATION_DELAY);
    });
  } catch (error) {
    console.error("Error getting fingerprint:", error);
    return DEFAULT_FINGERPRINT_PREFIX + Date.now();
  }
};
