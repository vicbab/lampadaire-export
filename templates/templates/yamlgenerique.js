let schema = [
  {label:'title_f', type: 'string',control:[ 
    {label:'title',rule:'stripMarkdown'}
  ]},
  {label:'subtitle_f', type: 'string',control:[
    {label:'subtitle',rule:'stripMarkdown'}
  ]},
  {label:'authors', type:'array',of:'people'},
  {label:'date', type: 'date',control:[
    {label:'year',rule:'split',delimiter:'/',group:0},
    {label:'month',rule:'split',delimiter:'/',group:1},
    {label:'day',rule:'split',delimiter:'/',group:2},
  ]},
  {label:'abstract', type:'array',of:[ 
    {label:'text_f',type:'text',control:[
      {label:'text',rule:'stripMarkdown'}
    ]},
    {label:'lang',type:'string',in:['fr','en','it','es','pt','de','uk','ar']}
  ]},
  {label:'keywords',type: 'array', of:[ 
    {label:'lang',in:['fr','en','it','es','pt','de','uk','ar']},
    {label:'list_f',control:[
	{label:'list',rule:'stripMarkdown'}]}
  ]},
  {label:'controlledKeywords',type:'array',of: [ // EDITEUR
    {label:'label',type:,'string'},
    {label:'idRameau', type:'string'},
    {label:'uriRameau', type:'string'}
  ]},
  {label:'lang',type:'string',in:['fr','en','it','es','pt','de','uk','ar']},
  {label:'id', type: 'string'}, // EDITEUR
  {label:'url_article', type: 'string'}, // EDITEUR
  {label:'typeArticle',type:'array',of:'string'}, // EDITEUR
  {label:'publisher', type: 'string'}, // EDITEUR
  {label:'journal', type: 'string'}, // EDITEUR
  {label:'issnnum', type: 'string'}, // EDITEUR
  {label:'directors', type:'array',of:'people'}, // EDITEUR
  {label:'prod', type: 'string'}, // EDITEUR
  {label:'prodnum', type: 'string'}, // EDITEUR
  {label:'diffnum', type: 'string'}, // EDITEUR
  {label:'rights', type: 'string'}, 
  {label:'dossier', type: 'array', of:[ // EDITEUR
    {label:'title', type:'string'},
    {label:'id', type:'string'}
  ]},
  {label:'issueDirectors',type:'array',of:'people'}, // EDITEUR
  {label:'reviewers',type:'array',of:'people'}, // EDITEUR
  {label:'translators',type:'array',of:'people'}, // EDITEUR
  {label:'transcriber',type:'array',of:'people'}, // EDITEUR
  {label:'translationOf',type:'array',of:[ // EDITEUR
    {label:'lang',type:'string',in:['fr','en','it','es','pt','de','uk','ar']},
    {label:'title',type:'string'},
    {label:'url',type:'string'}
  ]},
  {label:'bibliography', type: 'string'}, 
  {label:'link-citations', type: 'boolean'},  // EDITEUR (true par défaut)
  {label:'nocite',type:'string',in:['','@*']} 
]
