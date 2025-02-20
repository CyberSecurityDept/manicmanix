import IconGif from '../../assets/mute-muter.gif'
import plusSign from '../../assets/plus-sign.svg'

const ReconnectModel = ({ onClose }) => {
  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 font-aldrich"
      style={{
        background: 'rgba(0, 0, 0, 0.8)'
      }}
    >
      <div className="relative w-[801px] h-[422px] border border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] flex flex-col items-center justify-center p-8">
        {/* Plus Sign (Top Left) */}
        <img src={plusSign} alt="Plus Sign" className="absolute top-[-12px] left-[-12px] w-6 h-6" />

        {/* Plus Sign (Bottom Right) */}
        <img
          src={plusSign}
          alt="Plus Sign"
          className="absolute bottom-[-12px] right-[-12px] w-6 h-6"
        />

        {/* Icon Reconnect */}
        <img src={IconGif} alt="gif" className="w-[202px] h-[202px] mb-6" />

        {/* Connection Lost Text */}
        <h2 className="text-xl font-bold mb-4 text-[#C31C1C]">Connection Lost!</h2>

        {/* Additional Text */}
        <p className="text-white text-center mb-6">
          It looks like your device has been disconnected.
          <br />
          Please make sure the cable is properly connected and try again.
        </p>
      </div>
    </div>
  )
}

export default ReconnectModel
