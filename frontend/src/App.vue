<template>
  <div id="app" class="basic_style" :class="theme">
    <!-- 侧边栏 -->
    <aside class="side_bar">
      <!-- 顶部 UI -->
      <div class="side_top">
        <!-- 用户头像 -->
        <div class="user_avatar">
          <img v-if="avatar_url" :src="avatar_url" alt="用户头像">
          <div v-else class="no_avatar"></div>
        </div>
        <!-- 用户名 -->
        <div class="username">{{username}}</div>
      </div>

      <!-- 新增对话（按钮） -->
      <button class="add_chat" >
        <svg class="side_icon" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" width="16" height="16"><path d="M950.857143 438.857143H73.142857a73.142857 73.142857 0 1 0 0 146.285714h877.714286a73.142857 73.142857 0 0 0 0-146.285714z"></path><path d="M512 0a73.142857 73.142857 0 0 0-73.142857 73.142857v877.714286a73.142857 73.142857 0 1 0 146.285714 0V73.142857a73.142857 73.142857 0 0 0-73.142857-73.142857z" ></path></svg>
        <span class="side_text">创建新对话</span>
      </button>

      <!-- 聊天列表 -->
      <div class="chat_list">
        <div class="side_card">
          <svg class="side_icon" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" width="16" height="16"><path d="M512 938.666667c235.648 0 426.666667-191.018667 426.666667-426.666667S747.648 85.333333 512 85.333333 85.333333 276.352 85.333333 512s191.018667 426.666667 426.666667 426.666667z m0 85.333333C229.248 1024 0 794.752 0 512S229.248 0 512 0s512 229.248 512 512-229.248 512-512 512z m42.666667-486.869333V298.538667C554.666667 275.328 535.552 256 512 256c-23.722667 0-42.666667 19.029333-42.666667 42.538667v256.256a41.984 41.984 0 0 0 12.202667 29.866666l121.258667 121.258667a42.368 42.368 0 0 0 60.032-0.298667 42.666667 42.666667 0 0 0 0.298666-60.032L554.666667 537.130667z"></path></svg>
          <div class="side_text">聊天历史</div>
        </div>
      </div>

      <!-- 底部区域 -->
      <div class="side_bottom">
        <svg class="bottom_icon" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" width="28" height="28"><path d="M479.676 857.634c8.09 0.546 17.613 0.956 27.477 0.956H512c9.899 0 19.456-0.41 27.546-0.956l8.328-58.71a31.54 31.54 0 0 1 24.167-26.282 266.138 266.138 0 0 0 78.267-31.676 31.573 31.573 0 0 1 36.42 2.731l46.831 35.567c6.11-5.359 13.108-11.81 20.07-18.773l3.414-3.414c7.032-6.997 13.483-14.028 18.842-20.138l-35.499-47.31a31.54 31.54 0 0 1-1.468-35.668 264.875 264.875 0 0 0 32.461-75.64 31.437 31.437 0 0 1 26.692-25.873l59.563-8.158c0.546-8.09 0.956-17.579 0.956-27.443V512c0-9.899-0.41-19.456-0.956-27.58l-58.504-8.328a31.505 31.505 0 0 1-26.283-24.133 265.455 265.455 0 0 0-31.232-77.414 31.47 31.47 0 0 1 1.297-36.215l36.352-47.89a431.582 431.582 0 0 0-18.773-20.07l-3.414-3.413a433.084 433.084 0 0 0-20.138-18.842l-47.446 35.601a31.47 31.47 0 0 1-37.512 0.273 265.557 265.557 0 0 0-75.844-31.744 31.54 31.54 0 0 1-23.689-26.316l-8.158-59.563a429.466 429.466 0 0 0-27.443-0.956H512c-9.899 0-19.456 0.41-27.546 0.956l-8.328 58.71a31.505 31.505 0 0 1-26.42 26.726 265.42 265.42 0 0 0-76.048 31.163 31.437 31.437 0 0 1-36.66-2.901l-46.557-35.328c-6.11 5.359-13.108 11.776-20.07 18.773l-3.414 3.414a426.322 426.322 0 0 0-18.842 20.138l35.601 47.446a31.47 31.47 0 0 1 0 37.888 265.42 265.42 0 0 0-31.573 75.434 31.505 31.505 0 0 1-26.317 23.689l-59.46 8.192c-0.546 8.09-0.956 17.579-0.956 27.443V512c0 9.899 0.41 19.456 0.956 27.546l58.71 8.328a31.505 31.505 0 0 1 26.76 26.829l0.136 1.16c6.417 26.283 16.794 51.371 30.823 74.582a31.505 31.505 0 0 1-2.936 36.693l-35.157 46.421c5.393 6.076 11.81 13.108 18.773 20.07l3.414 3.414c7.065 7.032 14.097 13.483 20.172 18.842l47.446-35.601a31.505 31.505 0 0 1 39.219 1.024 265.42 265.42 0 0 0 74.103 30.72c12.527 3.072 21.914 13.517 23.689 26.282l8.192 59.324zM512 921.6h-4.847c-30.959 0-58.129-3.413-59.29-3.584a31.505 31.505 0 0 1-27.204-26.965l-8.772-63.693a327.885 327.885 0 0 1-56.525-23.962l-50.38 37.888a31.505 31.505 0 0 1-38.196-0.273c-0.887-0.717-22.528-17.51-44.441-39.39l-3.414-3.413c-21.88-21.88-38.673-43.52-39.39-44.442a31.505 31.505 0 0 1-0.17-38.297l38.912-51.337a328.533 328.533 0 0 1-23.04-56.832l-62.464-8.874a31.505 31.505 0 0 1-26.795-27.17c-0.17-1.127-3.584-28.331-3.584-59.256v-4.847c0-30.959 3.413-58.129 3.584-59.29a31.505 31.505 0 0 1 26.965-27.204l63.864-8.772a327.919 327.919 0 0 1 23.893-56.354l-37.956-50.518a31.505 31.505 0 0 1 0.239-38.229c0.717-0.887 17.51-22.528 39.39-44.441l3.413-3.414a519.339 519.339 0 0 1 44.442-39.356 31.505 31.505 0 0 1 38.297-0.204l51.473 39.082a327.885 327.885 0 0 1 56.662-22.971l8.874-62.635a31.505 31.505 0 0 1 27.205-26.829c1.126-0.205 28.33-3.618 59.255-3.618h4.847c30.959 0 58.129 3.413 59.29 3.584 14.097 1.81 25.258 12.868 27.204 26.965l8.738 63.966a328.05 328.05 0 0 1 56.32 23.86l50.586-38.025a31.47 31.47 0 0 1 38.229 0.239c0.887 0.717 22.528 17.51 44.441 39.39l3.414 3.413a518.963 518.963 0 0 1 39.356 44.442c8.704 11.264 8.806 26.965 0.17 38.331l-38.98 51.371a327.339 327.339 0 0 1 23.04 56.695l62.532 8.91a31.505 31.505 0 0 1 26.829 27.204c0.137 1.16 3.584 28.33 3.584 59.255v4.847c0 30.959-3.413 58.129-3.584 59.29a31.54 31.54 0 0 1-26.965 27.204l-63.796 8.738a327.475 327.475 0 0 1-23.893 56.422l37.888 50.518c8.533 11.332 8.397 26.965-0.273 38.195-0.683 0.887-17.476 22.528-39.356 44.441l-3.413 3.414a520.329 520.329 0 0 1-44.442 39.39 31.505 31.505 0 0 1-38.331 0.136l-51.508-39.048c-18.09 9.42-37.034 17.066-56.593 22.937l-8.874 62.737a31.505 31.505 0 0 1-27.205 26.83c-1.16 0.136-28.33 3.583-59.255 3.583z m0-518.11a108.783 108.783 0 0 0-108.646 108.647A108.783 108.783 0 0 0 512 620.783a108.749 108.749 0 0 0 108.646-108.646A108.783 108.783 0 0 0 512 403.49z m0 280.303a171.861 171.861 0 0 1-171.69-171.656A171.861 171.861 0 0 1 512 340.446a171.861 171.861 0 0 1 171.657 171.69A171.861 171.861 0 0 1 512 683.828z" ></path></svg>
        <svg class="bottom_icon" @click="change_theme" v-if="theme === 'dark'" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="9967" width="28" height="28"><path d="M439.04383639 224.33271976a289.43717504 289.43717504 0 0 0-89.06329676 39.44690807c-27.5075319 18.12412161-51.158867 39.64960558-70.96389486 64.57645191-19.79019562 24.92684633-35.31880082 53.25011237-46.62042137 84.97474006C221.10449032 445.05050411 215.45368042 478.01109252 215.45368042 512c0 40.16870887 7.81621301 78.48347702 23.45358166 115.04318192 15.64725682 36.67341315 36.77228986 68.19039996 63.2910532 94.76354538 26.53359488 26.56820206 58.11485196 47.57952611 94.69927585 63.23667111 36.59431134 15.65714501 75.00301286 23.48324474 115.16183354 23.48324475 33.97407594 0 66.85061917-5.56182137 98.62468557-16.89310498 31.76417894-11.32633953 60.10227581-26.77584294 85.01429133-46.65502781 24.87740834-19.77536407 46.43255539-43.46625042 64.57150781-70.96389488a290.15403174 290.15403174 0 0 0 39.43701989-88.98913905c-8.3056532 0.72180079-17.71378249 1.13213991-28.0958481 1.1321392-45.21637032 0-88.35138342-8.85936294-129.45942212-26.46932463-41.1327577-17.71872658-76.62459295-41.50848964-106.44089858-71.27535655C505.84007277 458.54719011 482.10963587 423.01086095 464.42057238 381.91765379 446.7562286 340.81455917 437.94135957 297.65977044 437.94135957 252.4483442c0-10.40184195 0.39550758-19.77536407 1.15685891-28.01674772l-0.049438-0.09887672zM512.02976157 141.21192041c8.32542811 0 16.51242896 0.31146168 24.6054972 0.92944167-16.4036648 35.32374419-24.60549719 72.09603405-24.60549719 110.30698212 0 35.12104668 6.84227598 68.69961578 20.58121076 100.83458258 13.70927096 32.03114601 32.15474243 59.63261126 55.35124448 82.80933769 23.16683898 23.17178306 50.76830423 41.60736635 82.82416923 55.30674985 32.02125855 13.69938351 65.654209 20.60098567 100.78514387 20.60098568 38.23072298 0 75.03267594-8.24138293 110.35147675-24.62032874 0.59326099 8.14250622 0.86517214 16.28006837 0.86517213 24.62032874 0 33.57856837-4.43956893 66.43533597-13.29893256 98.46648269-8.90880166 32.03114601-21.28817928 61.69419283-37.24195443 88.78149743-15.92411206 27.19112615-35.31880082 52.11797247-58.09013296 74.87941716-22.77627549 22.76144395-47.74267309 42.12152555-74.87447306 58.09013223-27.15157487 15.96366261-56.75529553 28.32326532-88.78644152 37.28644905A368.16784419 368.16784419 0 0 1 512.00009921 882.78807959a368.20739474 368.20739474 0 0 1-98.48625832-13.28904439c-32.03609009-8.95824037-61.6249792-21.31784236-88.79138561-37.28150569-27.12685589-15.96860669-52.08336529-35.32868827-74.89919206-58.09013223-22.7515565-22.76144395-42.13635709-47.68829101-58.05058169-74.87941715-15.96366261-27.0922487-28.34304097-56.75529553-37.2518426-88.78149744A367.9354836 367.9354836 0 0 1 141.21201889 512c0-33.57856837 4.4494571-66.43533597 13.30882004-98.46648269 8.90880166-32.03114601 21.28817928-61.69419283 37.25184259-88.78149744 15.91916798-27.19112615 35.29902519-52.11797247 58.0505817-74.87941715 22.81582676-22.86526476 47.77233617-42.22534634 74.89919206-58.09013223C351.89380578 175.81880789 381.4826949 163.36032846 413.51878498 154.50096479A368.20739474 368.20739474 0 0 1 512.00009921 141.21192041h0.02966236z" ></path></svg>
        <svg class="bottom_icon" @click="change_theme" v-else viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="11351" width="28" height="28"><path d="M752.41931153 240.7063601c8.36993432 0 15.62255883 3.08990502 21.72821045 9.16589356 6.1353147 6.08093262 9.18566918 13.3928833 9.18566918 21.73315382 0 8.55285621-3.05035376 15.85986352-9.18566918 21.94079614l-43.67394996 43.66900658c-5.93261719 5.97216773-13.17041016 8.95825195-21.72326709 8.95825195-8.87420678 0-16.20098901-2.98608422-22.08911085-8.75061035-5.88317847-5.87329102-8.80004906-13.2890625-8.80004906-22.14843774 0-8.54791283 2.95642114-15.75604272 8.91375732-21.72821044l43.66900659-43.67394996c6.14025879-6.07598853 13.44726539-9.16589356 21.98034668-9.16589356z m37.66223167 240.39459181h61.79809547c8.52813721 0 15.82031227 2.98608422 21.83697534 9.06207276C879.78271508 496.24395728 882.78857422 503.45208717 882.78857422 512c0 8.55285621-3.00585914 15.85986352-9.07196021 21.83697533-6.01666236 6.07598853-13.30883813 9.06207276-21.83697534 9.06207276h-61.79809547c-8.52813721 0-15.80053734-2.98608422-21.86663841-9.06207276-6.01666236-5.97711182-9.05712867-13.2890625-9.05712867-21.83697533 0-8.55285621 3.04046631-15.76098609 9.05712867-21.83697533 6.06610107-6.07598853 13.33850122-9.06207276 21.86663841-9.06207276zM512 141.21142578c8.52813721 0 15.79064917 3.08990502 21.85180688 9.06207276 6.02160645 6.08093262 9.05712867 13.3928833 9.05712867 21.83697533v61.79809546c0 8.55285621-3.03552222 15.85986352-9.0521853 21.83697534-6.06610107 6.07598853-13.32861305 9.16589356-21.85675025 9.16589355-8.53802467 0-15.80053734-3.08990502-21.86663842-9.16589355-6.01666236-5.97711182-9.0521853-13.2890625-9.05218458-21.83697534V172.11047387c0-8.44409203 3.03552222-15.76098609 9.05218458-21.83697533C496.20440674 144.3013308 503.46691871 141.21142578 512.00494408 141.21142578zM271.81304907 240.7063601c8.36499023 0 15.61267066 3.08990502 21.743042 9.16589356l43.66900659 43.67394996c6.14025879 6.07598853 9.17083764 13.38793922 9.17083764 21.72821044 0 8.55285621-3.01080323 15.86480689-9.05712938 21.83697534-6.03149391 6.08093262-13.30389404 9.06207276-21.85180617 9.06207275-8.69622827 0-16.02795386-2.98608422-21.95068359-8.85443115l-43.68383814-43.67395068c-5.97216773-5.97216773-8.92858886-13.28411842-8.92858886-22.03967284 0-8.55285621 3.00585914-15.76098609 9.07196021-21.83697462 6.01666236-5.97216773 13.30883813-9.06207276 21.85675096-9.06207276h-0.03955126z m436.93725586 436.91253615c8.36499023 0 15.60772729 2.98608422 21.72326709 9.16589355l43.67394995 43.67395067c6.1353147 6.17980933 9.18566918 13.38793922 9.18566919 21.93585205 0 8.34521461-3.05035376 15.65716529-9.18566919 21.73315382-6.1105957 6.17980933-13.35827613 9.16589356-21.72326636 9.16589356-8.52813721 0-15.84008789-2.98608422-21.98034668-9.16589356l-43.66900659-43.66900587c-5.95733618-5.87329102-8.91375732-13.1852417-8.91375732-21.73315453 0-8.55285621 3.01080323-15.86480689 9.05712866-21.94079614 6.03149391-6.07598853 13.32861305-9.16589356 21.85180689-9.16589355h-0.01977564zM512.00494408 388.40380836c-34.12243628 0-63.22192359 12.05310035-87.39239525 36.2532351-24.1358645 24.10125732-36.21368384 53.25018335-36.21368384 87.34295654 0 34.0927732 12.07782007 63.24169922 36.21368384 87.44677734C448.78796387 623.53814721 477.88250709 635.59619164 512 635.59619164c34.12243628 0 63.23181176-12.05310035 87.4072268-36.15435838C623.51837158 575.2466433 635.59619164 546.09771729 635.59619164 512c0-34.0927732-12.07782007-63.24169922-36.18896484-87.34295654C575.23181176 400.45690942 546.12243628 388.40380836 512 388.40380836zM172.12036133 481.10095191h61.79809547c8.53802467 0 15.80053734 2.98608422 21.86663841 9.06207276 6.01666236 6.08093262 9.05712867 13.2890625 9.05712867 21.83697533 0 8.55285621-3.04046631 15.85986352-9.05712867 21.83697533-6.06610107 6.07598853-13.32861305 9.06207276-21.86663841 9.06207276h-61.79809547c-8.52813721 0-15.81042481-2.98608422-21.83697534-9.06207276C144.21728492 527.85986352 141.21142578 520.54791283 141.21142578 512c0-8.55285621 3.00585914-15.76098609 9.07196021-21.83697533 6.03149391-6.07598853 13.30883813-9.06207276 21.83697534-9.06207276zM512.00494408 759.19238258c8.52813721 0 15.79064917 2.98608422 21.85180617 9.06207274 6.02160645 6.08093262 9.05712867 13.2890625 9.05712938 21.83697535v61.79809546c0 8.55285621-3.03552222 15.85986352-9.0521853 21.83697533C527.79559326 879.80249 520.53308129 882.78857422 512 882.78857422c-8.53802467 0-15.80053734-2.98608422-21.86663842-9.06207276-6.01666236-5.97711182-9.0521853-13.2890625-9.05218458-21.83697533v-61.79809546c0-8.55285621 3.03552222-15.76098609 9.05218458-21.83697534 6.06610107-6.07598853 13.32861305-9.06207276 21.86663842-9.06207275z m-196.47839379-81.57348633c8.5034182 0 15.80053734 2.98608422 21.84686279 9.16589355 6.03149391 6.08093262 9.07196021 13.3928833 9.07196021 21.94079614 0 8.44409203-3.08001685 15.65222192-9.19555664 21.72821044l-43.67394995 43.67394996c-6.10565162 6.17980933-13.34838867 9.16589356-21.72326637 9.16589356-8.54791283 0-15.84008789-2.98608422-21.85180687-8.96319533-6.07104516-6.07598853-9.0769043-13.38793922-9.0769043-21.93585205 0-8.65173364 2.95642114-15.96862769 8.92858887-21.94079614l43.68383813-43.66900658c6.10565162-6.17980933 13.44232202-9.16589356 21.95068359-9.16589355h0.03955054zM512 326.60571289c33.628052 0 64.6506958 8.34521461 93.0481565 24.81811547 28.42712378 16.69042992 50.92163109 39.1404419 67.4637456 67.56756568 16.57177758 28.32824708 24.86755347 59.32617188 24.86755347 93.00860596 0 33.68243408-8.27600098 64.68035888-24.86755347 93.10748267-16.58166504 28.32824708-39.08605981 50.77825904-67.4637456 67.4637456-28.36285424 16.58166504-59.37561059 24.82305884-93.0481565 24.82305884-33.66760254 0-64.67047143-8.24139381-93.05804468-24.81811547-28.37768578-16.69042992-50.86230492-39.14538598-67.46374487-67.46868897-16.58166504-28.42712378-24.86755347-59.42504859-24.86755348-93.10748267 0-33.68243408 8.31555152-64.68035888 24.86755348-93.00860596 16.55200195-28.42712378 39.03662109-50.87713647 67.46374487-67.56262231C447.35424828 334.94598413 478.371948 326.60571289 512 326.60571289z"></path></svg>
      </div>
    </aside>

    <!-- 主界面 -->
    <main class="main_interface">
      <!-- 下半部分 -->
      <div class="ask_interface">
        <!-- 输入框 -->
        <textarea class="main_question" v-model="question" />
        <div class="button_area_under_question">
          <svg v-if="more_setting" class="more_setting_icon" @click="change_more_setting" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="16" height="16"><path d="M854.016 739.328l-313.344-309.248-313.344 309.248q-14.336 14.336-32.768 21.504t-37.376 7.168-36.864-7.168-32.256-21.504q-29.696-28.672-29.696-68.608t29.696-68.608l376.832-373.76q14.336-14.336 34.304-22.528t40.448-9.216 39.424 5.12 31.232 20.48l382.976 379.904q28.672 28.672 28.672 68.608t-28.672 68.608q-14.336 14.336-32.768 21.504t-37.376 7.168-36.864-7.168-32.256-21.504z" ></path></svg>
          <svg v-else class="more_setting_icon" @click="change_more_setting" viewBox="0 0 1026 1024" xmlns="http://www.w3.org/2000/svg" width="16" height="16"><path d="M857.088 224.256q28.672-28.672 69.12-28.672t69.12 28.672q29.696 28.672 29.696 68.608t-29.696 68.608l-382.976 380.928q-12.288 14.336-30.72 19.968t-38.912 4.608-40.448-8.704-34.304-22.016l-376.832-374.784q-29.696-28.672-29.696-68.608t29.696-68.608q14.336-14.336 32.256-21.504t36.864-7.168 37.376 7.168 32.768 21.504l313.344 309.248z"></path></svg>
          <div class="sending_area">
  <button class="sending_button" @click="send(false)" :disabled="loading">
    {{ loading ? '发送中...' : '发送' }}
  </button>
  <button class="generate_button" @click="send(true)" :disabled="loading">
    {{ loading ? '生成中...' : '生成' }}
  </button>
  <!-- 新增取消按钮 -->
  <button class="cancel_button" @click="cancelRequest()" v-if="loading">取消</button>
</div>
        </div>
      </div>

      <!-- 更多选项界面 -->
      <div class="more_setting" v-if="more_setting">
        <div class="setting_column">
          <div class="setting_text">文档目录</div>
          <textarea class="setting_textarea" v-model="menu"></textarea>
          <div class="setting_text">文档提纲</div>
          <textarea class="setting_textarea" v-model="outline"></textarea>
          <div class="setting_text">文档示例段落</div>
          <textarea class="setting_textarea" v-model="example"></textarea>
        </div>
        <div class="setting_column">
          <div class="setting_text">预期文档字数</div>
          <input class="setting_input" type="number" v-model.number="file_num" min="100" max="10000"/>

          <div class="setting_text">预期文档文风</div>
          <select class="setting_select" v-model="style">
            <option value="不指定">不指定</option>
            <option value="技术说明">技术说明</option>
            <option value="学术论文">学术论文</option>
            <option value="营销">营销</option>
            <option value="新闻">新闻</option>
            <option value="日常">日常</option>
          </select>

          <div class="setting_text">面向受众</div>
          <select class="setting_select" v-model="facing">
            <option value="不指定">不指定</option>
            <option value="技术人员">技术人员</option>
            <option value="学生">学生</option>
            <option value="客户">客户</option>
            <option value="观众">观众</option>
            <option value="平时聊天对象">平时聊天对象</option>
          </select>

          <div class="drop_zone" @dragover.prevent="onDragOver" @dragleave.prevent="onDragLeave" @drop.prevent="onDrop" @click="triggerFileInput">
            <div v-if="no_file" class="drop_zone_text">点击或拖动文件至此以上传</div>
          </div>

        </div>
      </div>

      <!-- 上半部分 -->
      <div v-if="welcome" class="chat_area">
        <!-- 欢迎界面 -->
        <div v-if="welcome" class="welcome_sentence" >
          您有什么想探讨的？
        </div>
        <!-- 聊天记录 -->
        <div v-else class="chat_list">
  <div v-for="(message, index) in messages" :key="index" :class="`msg_item ${message.role}`">
    <!-- 加载提示（机器人思考中） -->
    <span v-if="message.thinking" class="thinking_text">{{ message.thinking }}</span>
    <!-- 消息内容 -->
    <div class="msg_content">{{ message.content }}</div>
  </div>
</div>
      </div>

    </main>
  </div>
</template>


<script>
export default {
  name: 'App',
  data() {
    return {
      /* 用户信息方面 */
      username: '管理员',
      user_id: '',
      user_email: '',
      avatar_url: '',
      /* 样式方面 */
      theme: 'dark',
      more_setting: false,
      /* 欢迎界面 */
      welcome: true,
      /* 输入框 */
      question: '',
      menu: '',
      outline: '',
      example: '',
      file_num: '1000',
      style: '不指定',
      facing: '不指定',
      docFiles: [],
      /* 加载状态 */
      loading: false,
      error: null,
      /* 聊天信息 */
      messages: [],
      conversation_id: '',
      uploads: [],
      ready: null,
      answer: null,
      currentAbortController: null,
      /* 上传文件 */
      uploadPromises: [],
      no_file: true,
      fileDropOver: false,
    }
  },
  watch: {
    messages: {

    }
  },
  methods: {
    // 切换主题
    change_theme() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', this.theme)
    },
    // 切换更多选项
    change_more_setting() {
      this.more_setting = !this.more_setting;
    },
    // 拖拽文件至上方
    onDragOver() {
      this.fileDropOver = true;
    },
    // 拖拽文件离开上方
    onDragLeave() {
      this.fileDropOver = false;
    },
    // 放置文件
    onDrop(e) {
      this.fileDropOver = false;
      const data = e.dataTransfer;
      if (!data) return;

      // 获取文件转为数组
      const files = Array.from(data.files || []);
      if (files.length) {
        for (const f of files) {
          const p = this.uploadAndAppend(f);
          print("[187]文件ID:", p); //调试用
          this.uploadPromises.push(p);
        }
      }
    },
    // 上传文件并添加到列表
    async uploadAndAppend(file) {
      const placeholder = {
        name: file.name,
        size: file.size,
        type: file.type,
        uploading: true,
        upload_file_id: null
      };
      const index = this.docFiles.length; // 获取索引
      this.docFiles.push(placeholder);

      // 构建请求体
      const form = new FormData();
      form.append('file', file, file.name);
      form.append('user', this.username);

      // 发送请求
      const res = await fetch('/api/upload', {method: 'POST', body: form});
      // 处理错误
      if (!res.ok) {
        console.error("发送请求失败, 文件名:", file.name, "，用户:" , this.username)
        const text = await res.text();
        console.error("错误信息:", text);
        this.docFiles[index].uploading = false;
        this.docFiles[index].error = text;
        return null; // 不抛出错误
      }
      // 解析响应
      const json = await res.json();
      const upload_file_id = json.upload_file_id || json.id || null;
      // 更新状态
      this.docFiles[index].upload_file_id = upload_file_id;
      this.docFiles[index].uploading = false;
      // 返回给 Promise 队列
      return upload_file_id;
    },

    // 发送消息
    async send(create_docx = false) {
      const q = this.question;
      if (!q || this.loading) return;

      this.welcome=false;

      this.question = '';
      this.answer = null;

      // 添加玩家问题和空返回
      this.messages.push({role: 'user', content: q});
      this.messages.push({role: 'bot', content: '', thinking: '正在思考中...'});
      const botIdx = this.messages.length - 1;

      // 清除之前中断导致的空消息
      for (let i = this.messages.length-1; i >= 0; i--) {
        if (this.messages[i].role === 'bot' && (!this.messages[i].content || this.messages[i].content.trim() === '')) {
          this.messages.splice(i, 1);
        } else break;
      }

      //标记加载状态
      this.loading = true;
      // 创建新的 AbortController, 便于取消请求（用户点取消按钮)
      const controller = new AbortController();
      this.currentAbortController = controller;

      // 等待文件上传
      if (this.uploadPromises && this.uploadPromises.length) {
        await Promise.allSettled(this.uploadPromises);
        this.uploadPromises = [];
      }

      // 构建payload(请求参数)
      const payload = {
        question: q,
        stream: true,
        docx_create: create_docx,
        menu: this.menu,
        outline: this.outline,
        example: this.example,
        file_num: this.file_num,
        style: this.style,
        facing: this.facing,
        docFiles: this.docFiles,}；

      //发送请求
      const response = await fetch('/api/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal, // 关联AbortController，支持取消请求
    });

    // 校验请求是否成功
    if (!response.ok) {
      throw new Error(`请求失败：${response.status} ${response.statusText}`);
    }

    //  处理流式响应（核心：逐字渲染回答，提升用户体验）
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let botContent = ''; // 拼接机器人回答

    while (true) {
      // 检查是否有取消请求的信号
      if (controller.signal.aborted) {
        throw new Error('请求已取消');
      }

      const { done, value } = await reader.read();
      if (done) break;

      // 解码流式数据并拼接（根据后端返回格式调整，比如JSON/纯文本）
      const chunk = decoder.decode(value, { stream: true });
      botContent += chunk;

      //  实时更新页面：把拼接的内容赋值给bot占位消息
      this.messages[botIdx].content = botContent;
      this.messages[botIdx].thinking = ''; // 清空加载提示
    }

    //  最终确认：保存完整回答（可选）
    this.answer = botContent;

    // 如果需要生成docx，这里可补充下载逻辑
    if (create_docx) {
      // 示例：调用下载接口
      // await this.downloadDocx(botContent);
    }

  }

  //  最终清理：无论成功/失败，都重置加载状态和AbortController
    this.loading = false;
    // 只有当前controller和保存的一致时才清空（避免取消其他请求）
    if (this.currentAbortController === controller) {
      this.currentAbortController = null;
    }
  }
},

// 可选：添加取消请求的方法（比如用户点击“取消”按钮调用）
cancelRequest() {
  if (this.currentAbortController) {
    this.currentAbortController.abort(); // 触发请求取消
    this.currentAbortController = null;
    this.loading = false;
    // 找到最后一个bot消息，更新提示
    const lastBotMsg = this.messages.findLast(msg => msg.role === 'bot');
    if (lastBotMsg) {
      lastBotMsg.content = '请求已取消';
      lastBotMsg.thinking = '';
    }
  }
}
      }
    }
  },
}

</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 基本样式 */
.basic_style {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: auto;
  background: var(--bg);
}

/* 亮色主题 */
.light {
  --main_bg: #FAFEFF;
  --side_bg: #f7fcff;
  --side_border: #e5f3ff;
  --add_chat: #FAFEFF;
  --side_text: #020202;
  --icon: #020202;
  --bottom_icon: #020202;
  --box_shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  --ask_words: #000000;
  --sending_button: #E3EFFD;
  --generate_button: #FDDEA8;
  --setting_text: #020202;
  --setting_textarea_border: #e5f3ff;
  --setting_textarea_background: #f7fcff;
}

/* 暗色主题 */
.dark {
  --main_bg: #171717;
  --side_bg: #212121;
  --side_border: #383838;
  --add_chat: #2c2c2c;
  --side_text: #c4c4c4;
  --icon: #c4c4c4;
  --bottom_icon: #8c8c8c;
  --box_shadow: none;
  --ask_words: #ffffff;
  --sending_button: #212121;
  --generate_button: #FDDEA8;
  --setting_text: #c4c4c4;
  --setting_textarea_border: #383838;
  --setting_textarea_background: #212121;
}


/* 侧边栏主题 */
.side_bar {
  width: 250px;
  padding: 30px 12px 12px 12px;
  background: var(--side_bg);
  border-right: 1px solid var(--side_border);
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
}
.side_top {
  padding-left: 5px;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.username {
  font-size: 14px;
  font-weight: bold;
  color: var(--side_text);
  transition: all 0.2s ease;
}
.user_avatar {
  width: 25px;
  height: 25px;
  border-radius: 50%;
  overflow: hidden;
  background: #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}
.user_avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 保持比例裁剪 */
}
.add_chat {
  width: 100%;
  height: 40px;
  padding-left: 10px;
  margin-bottom: 5px;
  background: var(--add_chat);
  border: 1px solid var(--side_border);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s ease;
}
.side_card {
  width: 100%;
  height: 40px;
  padding-left: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.side_text {
  font-size: 14px;
  color: var(--side_text);
  transition: all 0.2s ease;
}
.side_bottom {
  margin-top: auto;
  padding-top: 20px;
}
.side_icon {
  fill: var(--icon);
  transition: all 0.2s ease;
}
.bottom_icon {
  fill: var(--bottom_icon);
  padding-left: 5px;
  transition: all 0.2s ease;
}

/* 主界面主题 */
.main_interface {
  flex: 1; /* flex: 1表示占满其余空间 */
  background: var(--main_bg);
  overflow: hidden;
  display: flex;
  flex-direction: column-reverse;
  align-items: center;
  transition: all 0.2s ease;
}
/* 消息区域 */
.chat_area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.welcome_sentence {
  font-size: 40px;
  color: var(--side_text);
  font-weight: bolder;
  font-family: '黑体', Courier, monospace;
  transition: all 0.2s ease;
}
.ask_interface {
  width: 90%;
  height: 20%;
  margin: 10px;
  background: var(--add_chat);
  border: 1px solid var(--side_border);
  border-radius: 8px;
  box-shadow: var(--box_shadow);
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
}
.main_question {
  width: 100%;
  height: 70%;
  margin: 0 0 10px 0;
  padding: 15px 20px 0 20px;
  background: none;
  border: none;
  overflow: auto;
  resize: none;
  scrollbar-width: none;

  text-align: left;
  vertical-align: top;
  outline: none;
  color: var(--ask_words);
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 16px;
  font-family: "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
  transition: all 0.2s ease;

}
.button_area_under_question {
  width: 100%;
  height: 30%;
  padding: 0 10px 10px 20px;
  display: flex;
  flex-direction: row;
}
.more_setting_icon {
  margin-top: 10px;
  fill: var(--icon);
  cursor: pointer;
  transition: all 0.2s ease;
}
.sending_area {
  margin-left: auto;
  display: flex;
  flex-direction: row;
  gap: 10px;
}
.sending_button {
  width: 100px;
  height: 100%;
  background: var(--sending_button);
  border: none;
  border-radius: 8px;

  font-size: 16px;
  font-family: "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
  color: var(--ask_words);
  cursor: pointer;
  transition: all 0.2s ease;
}
.generate_button {
  width: 100px;
  height: 100%;
  background: var(--generate_button);
  border: none;
  border-radius: 8px;

  font-size: 16px;
  font-family: "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
  color: #020202;
  cursor: pointer;
  transition: all 0.2s ease;
}
.more_setting {
  width: 90%;
  height: 50%;
  margin: 10px;
  padding: 15px;
  background: var(--add_chat);
  border: 1px solid var(--side_border);
  border-radius: 8px;
  box-shadow: var(--box_shadow);
  display: flex;
  flex-direction: row;
  gap: 20px;
  transition: all 0.2s ease;
}
.setting_column {
  width: 50%;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.setting_text {
  margin: 0 0 5px 0;
  font-size: 20px;
  font-weight: bold;
  color: var(--setting_text);
  transition: all 0.2s ease;
}
.setting_textarea {
  width: 100%;
  height: 150px;
  margin: 0 0 20px 0;
  background: var(--setting_textarea_background);
  border: 1px solid var(--setting_textarea_border);
  border-radius: 8px;
  overflow: auto;
  resize: none;
  scrollbar-width: none;

  text-align: left;
  vertical-align: top;
  outline: none;
  color: var(--ask_words);
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 16px;
  font-family: "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
  cursor: pointer;
  transition: all 0.2s ease;
}
.setting_input {
  height: 30px;
  margin: 0 0 20px 0;
  background: var(--setting_textarea_background);
  border: 1px solid var(--setting_textarea_border);
  border-radius: 4px;

  color: var(--ask_words);
  font-size: 16px;
  font-family: "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
  cursor: pointer;
  transition: all 0.2s ease;
}
.setting_select {
  height: 30px;
  margin: 0 0 20px 0;
  background: var(--setting_textarea_background);
  border: 1px solid var(--setting_textarea_border);
  border-radius: 4px;

  color: var(--ask_words);
  font-size: 16px;
  font-family: "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
  cursor: pointer;
  transition: all 0.2s ease;
}
.setting_select option {
  height: 30px;
  background: var(--setting_textarea_background);
  color: var(--ask_words);
  cursor: pointer;
  transition: all 0.2s ease;
}
.drop_zone {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  background: none;
  border: 2px solid var(--setting_textarea_border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.drop_zone_text {
  color: var(--ask_words);
  font-size: 16px;
  font-family: "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
}
</style>
