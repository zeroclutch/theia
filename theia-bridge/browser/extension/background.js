// event to run execute.js content when extension's button is clicked
// chrome.webNavigation.onCommitted.addListener(injectScript);

// async function injectScript() {
//   console.log("Injecting cursor.js")
//   const tabId = await getTabId();
//   chrome.scripting.executeScript({
//     target: {tabId: tabId},
//     files: ['cursor.js']
//   })
// }

async function exit() {
    return null
}

async function getTabId() {
  const tabs = await chrome.tabs.query({active: true, currentWindow: true});
  return (tabs.length > 0) ? tabs[0].id : null;
}

