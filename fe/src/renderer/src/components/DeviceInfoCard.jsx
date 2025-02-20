import React from 'react';

const DeviceInfoCard = ({
  plusSign,
  image,
  model,
  imei1,
  imei2,
  androidVersion,
  lastScan,
  securityPatch,
  serialNumber,
}) => {
  return (
    <div className="flex-1 relative">
      {/* Plus Sign at the border */}
      <img
        src={plusSign}
        alt="Device Image"
        className="absolute top-[-12px] left-[-12px] w-6 h-6"
      />
      <img
        src={plusSign}
        alt="Device Image"
        className="absolute bottom-[-11px] right-[-11px] w-6 h-6"
      />

      <div className="w-full h-[540px] max-h-[540px] border border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] text-white flex flex-col items-center justify-center p-4 overflow-y-auto">
        {/* Title Section */}
        <div className="text-center mb-4">
          <h2 className="text-3xl font-bold">Device Specification</h2>
        </div>

        {/* Device Image */}
        <img
          src={image}
          alt="Device"
          className="w-[250px] h-[160px] object-contain mb-4"
        />

        {/* Device Information */}
        <div className="text-left w-full max-w-md ">
          <p className="mb-2">
            <strong>Model :</strong> {model}
          </p>
          <p className="mb-2">
            <strong>Serial Number :</strong> {serialNumber}
          </p>
          <p className="mb-2">
            <strong>IMEI 1 :</strong> {imei1}
          </p>
          <p className="mb-2">
            <strong>IMEI 2 :</strong> {imei2}
          </p>
          <p className="mb-2">
            <strong>Android Version :</strong> {androidVersion}
          </p>
          <p className="mb-2">
            <strong>Security Patch :</strong> {securityPatch}
          </p>
          <p className="mb-2">
            <strong>Last Scan :</strong> {lastScan}
          </p>
        </div>
      </div>
    </div>
  );
};

export default DeviceInfoCard;
