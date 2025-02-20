export const createIframe = (url, options = {}) => {
  return {
    url,
    options: {
      ...options,
      sandbox: 'allow-same-origin allow-scripts allow-popups allow-forms',
      loading: 'lazy',
      allowFullScreen: true,
    }
  }
}

export const iframeEvents = {
  onLoad: (callback) => ({
    onLoad: callback
  }),
  onError: (callback) => ({
    onError: callback
  })
}