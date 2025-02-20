import React from 'react'
import PropTypes from 'prop-types'

const CustomIframe = ({ type, source, options, events }) => {
  const iframeStyle = {
    width: '100%',
    height: '100%',
    border: 'none',
    position: 'absolute',
    top: 0,
    left: 0,
    ...options?.style
  }

  if (type === 'webview') {
    return (
      <webview
        src={source}
        {...options}
        style={iframeStyle}
        {...events}
      />
    )
  }

  return (
    <iframe
      src={source}
      {...options}
      style={iframeStyle}
      {...events}
    />
  )
}

CustomIframe.propTypes = {
  type: PropTypes.oneOf(['iframe', 'webview']).isRequired,
  source: PropTypes.string.isRequired,
  options: PropTypes.object,
  events: PropTypes.object
}

CustomIframe.defaultProps = {
  options: {},
  events: {}
}

export default CustomIframe