// CodeMirror 6 editor for Python with LeetCode-like keys.
import {
  EditorView, EditorState, Prec, keymap, lineNumbers, highlightActiveLine, highlightActiveLineGutter, drawSelection,
  defaultKeymap, history, historyKeymap, indentWithTab, indentUnit, bracketMatching, syntaxHighlighting,
  defaultHighlightStyle, indentOnInput, closeBrackets, closeBracketsKeymap, python, oneDark,
} from "../vendor/codemirror.js";

const dark = () => document.documentElement.dataset.theme !== "light"
  && (document.documentElement.dataset.theme === "dark" || matchMedia("(prefers-color-scheme: dark)").matches);

// oneDark on the page surface: the darker background lifts its token colours above 4.5:1 contrast.
const darkSurface = EditorView.theme({
  "&": { backgroundColor: "var(--surface)" },
  ".cm-gutters": { backgroundColor: "var(--surface)", borderRight: "1px solid var(--line)" },
  ".cm-activeLine, .cm-activeLineGutter": { backgroundColor: "rgba(255, 255, 255, .035)" },
}, { dark: true });

export function createEditor(parent, { doc, onChange, onRun, onSubmit }) {
  const keys = Prec.highest(keymap.of([
    { key: "Mod-Enter", run: () => (onRun?.(), true) },
    { key: "Mod-Shift-Enter", run: () => (onSubmit?.(), true) },
    { key: "Mod-'", run: () => (onSubmit?.(), true) },
  ]));
  const view = new EditorView({
    parent,
    state: EditorState.create({
      doc,
      extensions: [
        keys,
        lineNumbers(),
        highlightActiveLineGutter(),
        highlightActiveLine(),
        drawSelection(),
        history(),
        indentOnInput(),
        bracketMatching(),
        closeBrackets(),
        indentUnit.of("    "),
        EditorState.tabSize.of(4),
        python(),
        dark() ? [oneDark, Prec.highest(darkSurface)] : syntaxHighlighting(defaultHighlightStyle),
        keymap.of([...closeBracketsKeymap, ...defaultKeymap, ...historyKeymap, indentWithTab]),
        EditorView.contentAttributes.of({ "aria-label": "Редактор кода на Python" }),
        // A phone screen is too narrow for sideways scrolling: long lines wrap instead.
        matchMedia("(max-width: 820px)").matches ? EditorView.lineWrapping : [],
        EditorView.updateListener.of((u) => u.docChanged && onChange?.(u.state.doc.toString())),
        EditorView.theme({
          "&": { height: "100%", fontSize: "14px" },
          ".cm-scroller": { fontFamily: "var(--mono)", lineHeight: "1.55" },
        }),
      ],
    }),
  });
  return {
    view,
    get value() {
      return view.state.doc.toString();
    },
    set value(text) {
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: text } });
    },
    focus: () => view.focus(),
  };
}
