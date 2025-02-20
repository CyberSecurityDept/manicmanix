// assets.js (JavaScript)

/**
 * Mengambil path dari file aset menggunakan URL yang benar.
 * @param {string} name - Nama file aset (misalnya: 'bg-darkmode.png')
 * @returns {string} - URL absolut ke aset
 */
export const getAsset = (name) => {
    // Menggunakan new URL untuk mendapatkan URL absolut berdasarkan import.meta.url
    return new URL(`../assets/${name}`, import.meta.url).href;
  };
  