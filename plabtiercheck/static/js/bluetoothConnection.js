<script>
  document.getElementById('connectBluetooth').addEventListener('click', function() {
    if (!navigator.bluetooth) {
      alert("Web Bluetooth is not available in this browser.");
      console.error("Web Bluetooth is not available in this browser.");
      return;
    }

    alert("Web Bluetooth is available in this browser.");

    navigator.bluetooth.requestDevice({
      acceptAllDevices: true
    })
    .then(device => {
      alert('장치 선택됨: ' + device.name);
      console.log('장치 선택됨:', device.name);
      return device.gatt.connect();
    })
    .then(server => {
      alert('블루투스 장치에 연결되었습니다: ' + server);
      console.log('블루투스 장치에 연결되었습니다:', server);
      // 여기서 추가적인 서비스 및 특성 작업 수행
    })
    .catch(error => {
      alert('블루투스 연결 중 오류 발생: ' + error);
      console.error('블루투스 연결 중 오류 발생:', error);
    });
  });
</script>
