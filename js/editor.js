// CodeMirror 6 editor for Python with LeetCode-like keys.
import {
  EditorView, EditorState, Prec, keymap, lineNumbers, highlightActiveLine, highlightActiveLineGutter, drawSelection,
  defaultKeymap, history, historyKeymap, indentWithTab, indentUnit, bracketMatching, syntaxHighlighting,
  defaultHighlightStyle, indentOnInput, closeBrackets, closeBracketsKeymap, python, oneDark,
} from "../vendor/codemirror.js";

const dark = () => document.documentElement.dataset.theme !== "light"
  && (document.documentElement.dataset.theme === "dark" || matchMedia("(prefers-color-scheme: dark)").matches);

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
        dark() ? oneDark : syntaxHighlighting(defaultHighlightStyle),
        keymap.of([...closeBracketsKeymap, ...defaultKeymap, ...historyKeymap, indentWithTab]),
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
