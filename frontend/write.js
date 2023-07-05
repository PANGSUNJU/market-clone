const form = document.getElementById("write-form");

const handleSubmitForm = async (event) => {
  // 이벤트 전파 방지 정도
  event.preventDefault();
  const body = new FormData(form);
  body.append("insertAt", new Date().getTime());
  try {
    const res = await fetch("/items", {
      method: "POST",
      body,
    });
    const data = await res.json();
    if (data === "200") window.location.pathname = "/";
  } catch (e) {
    console.error("이미지 업로드에 실패했습니다.");
  }
  // const res = await fetch("/items", {
  //   method: "POST",
  //   body: new FormData(form),
  // });
  // const data = await res.json();
  // if(data === '200') window.location.pathname="/";
  // else console.error("이미지 업로드에 실패했습니다.")
};

form.addEventListener("submit", handleSubmitForm);

//폼데이터 보낼땐 세계시간 기준으로 처리할땐 한국시간으로 받아져 시간이 맞지 않는 일이 종종발생할 수 있음
